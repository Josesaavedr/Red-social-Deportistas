from fastapi import FastAPI, APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session # , joinedload # Importar joinedload si se van a cargar relaciones anidadas
from typing import List

# Importa los módulos de base de datos y modelos
from . import models, database, auth

app = FastAPI()

# La creación de tablas ahora se gestiona con Alembic.
# @app.on_event("startup")
# def on_startup():
#     models.Base.metadata.create_all(bind=database.engine)

# Crea una instancia del router para organizar los endpoints
# Esquema para autenticación opcional
oauth2_scheme_optional = OAuth2PasswordBearer(tokenUrl="token", auto_error=False)

router = APIRouter()

@app.get("/")
def read_root():
    return {"message": "Servicio de Actividades en funcionamiento."}

@app.get("/health")
def health_check():
    """Endpoint de salud para verificar el estado del servicio."""
    return {"status": "ok"}

# Endpoint para obtener todas las actividades
@router.get("/activities/", response_model=List[models.Activity]) # Modificado para incluir author_name
def read_activities(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(database.get_db),
    token: Optional[str] = Depends(oauth2_scheme_optional) # Autenticación opcional para likes
):
    """
    Obtiene una lista de actividades de la base de datos.
    """
    activities = db.query(models.ActivityDB).offset(skip).limit(limit).all()
    
    # Obtener IDs de autores únicos para una sola llamada al servicio de usuarios
    author_ids = list(set(activity.author_id for activity in activities))
    users_data = {}
    if author_ids:
        try:
            # Asumiendo un endpoint en el servicio de usuarios para obtener múltiples usuarios por ID
            # Para simplificar, haremos llamadas individuales por ahora, pero esto es ineficiente para muchos usuarios.
            for author_id in author_ids:
                user_response = requests.get(f"{USERS_SVC_URL}/api/v1/users/{author_id}")
                user_response.raise_for_status()
                users_data[author_id] = user_response.json().get("username", f"Usuario {author_id}")
        except requests.exceptions.RequestException:
            pass # Manejar errores, por ahora simplemente no se asigna el nombre

    # Enriquecer las actividades con el nombre del autor y el estado del like
    # Se usa una función auxiliar para evitar duplicar código
    return [_enrich_activity_with_user_data(db, activity, users_data, token) for activity in activities]

# Endpoint para contar el total de actividades
@router.get("/activities/count")
def count_activities(db: Session = Depends(database.get_db)):
    """
    Cuenta el número total de actividades en la base de datos.
    """
    return {"total": db.query(models.ActivityDB).count()}

# Endpoint para obtener una actividad específica por su ID
@router.get("/activities/{activity_id}", response_model=models.Activity) # Modificado para incluir author_name
def read_activity(
    activity_id: int, 
    db: Session = Depends(database.get_db), 
    token: Optional[str] = Depends(oauth2_scheme_optional) # Autenticación opcional para likes
):
    """
    Obtiene los detalles de una actividad específica por su ID.
    Si se proporciona un token de autenticación, también indica si el usuario actual
    ha dado "Me gusta" a la actividad.
    """
    db_activity = db.query(models.ActivityDB).filter(models.ActivityDB.id == activity_id).first()
    if db_activity is None:
        raise HTTPException(status_code=404, detail="Activity not found")

    return _enrich_activity_with_user_data(db, db_activity, {}, token)

# Endpoint para crear una nueva actividad
@router.post("/activities/", response_model=models.Activity, status_code=status.HTTP_201_CREATED)
def create_activity(activity: models.ActivityCreate, db: Session = Depends(database.get_db)):
    """
    Crea una nueva actividad y la guarda en la base de datos.
    """
    # El author_id se obtiene del token en el frontend, y el backend lo usa para crear la actividad.
    # Este endpoint necesita current_user_id como dependencia.
    raise NotImplementedError("This endpoint needs to be updated to use current_user_id from auth.get_current_user_id")

# Endpoint para crear una nueva actividad (actualizado con autenticación)
@router.post("/activities/", response_model=models.Activity, status_code=status.HTTP_201_CREATED)
def create_activity(
    activity: models.ActivityCreate, 
    db: Session = Depends(database.get_db),
    current_user_id: int = Depends(auth.get_current_user_id)
):
    """
    Crea una nueva actividad y la guarda en la base de datos.
    El autor se obtiene del token de autenticación.
    """
    db_activity = models.ActivityDB(**activity.dict(), author_id=current_user_id)
    db.add(db_activity)
    db.commit()
    db.refresh(db_activity)
    return _enrich_activity_with_user_data(db, db_activity, {}, None) # No necesitamos token para el like en la creación

# Endpoint para actualizar una actividad
@router.put("/activities/{activity_id}", response_model=models.Activity)
def update_activity(
    activity_id: int, 
    activity: models.ActivityUpdate, 
    db: Session = Depends(database.get_db),
    current_user_id: int = Depends(auth.get_current_user_id)
):
    """
    Actualiza una actividad existente en la base de datos.
    Solo el autor original puede actualizar su actividad.
    """
    db_activity = db.query(models.ActivityDB).filter(models.ActivityDB.id == activity_id).first()
    if db_activity is None:
        raise HTTPException(status_code=404, detail="Activity not found")
    if db_activity.author_id != current_user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to update this activity")

    # Obtiene los datos del modelo Pydantic que no son None
    update_data = activity.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_activity, key, value)
    
    db.commit()
    db.refresh(db_activity)
    return _enrich_activity_with_user_data(db, db_activity, {}, None) # No necesitamos token para el like en la actualización

# Endpoint para dar "Me gusta" a una actividad (registra un LikeDB)
@router.post("/activities/{activity_id}/like", response_model=models.Like, status_code=status.HTTP_201_CREATED)
def like_activity(
    activity_id: int, 
    db: Session = Depends(database.get_db),
    current_user_id: int = Depends(auth.get_current_user_id)
):
    """
    Registra un "Me gusta" para una actividad por un usuario específico.
    Crea una entrada en la tabla 'likes' y actualiza el contador de likes de la actividad.
    El usuario se obtiene del token de autenticación.
    """
    # 1. Verificar si la actividad existe
    db_activity = db.query(models.ActivityDB).filter(models.ActivityDB.id == activity_id).first()
    if db_activity is None:
        raise HTTPException(status_code=404, detail="Activity not found")
    
    # 2. Verificar si el usuario ya dio "Me gusta" a esta actividad
    existing_like = db.query(models.LikeDB).filter(
        models.LikeDB.activity_id == activity_id,
        models.LikeDB.user_id == current_user_id
    ).first()

    if existing_like:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User already liked this activity")

    # 3. Crear el nuevo "Me gusta"
    db_like = models.LikeDB(activity_id=activity_id, user_id=current_user_id)
    db.add(db_like)
    
    # 4. Incrementar el contador de likes en la actividad (manteniendo la redundancia por ahora)
    db_activity.likes += 1

    db.commit()
    db.refresh(db_like)
    db.refresh(db_activity) # Refrescar la actividad para que el contador de likes esté actualizado si se usa en la respuesta
    return db_like

# Endpoint para eliminar un "Me gusta" de una actividad
@router.delete("/activities/{activity_id}/like", status_code=status.HTTP_204_NO_CONTENT)
def unlike_activity(
    activity_id: int, 
    db: Session = Depends(database.get_db),
    current_user_id: int = Depends(auth.get_current_user_id)
):
    """
    Elimina un "Me gusta" de una actividad por un usuario específico.
    """
    db_like = db.query(models.LikeDB).filter(
        models.LikeDB.activity_id == activity_id,
        models.LikeDB.user_id == current_user_id
    ).first()

    if db_like is None:
        raise HTTPException(status_code=404, detail="Like not found for this activity and user")

    db.delete(db_like)
    # Decrementar el contador de likes en la actividad (manteniendo la redundancia por ahora)
    db.query(models.ActivityDB).filter(models.ActivityDB.id == activity_id).update({"likes": models.ActivityDB.likes - 1})
    db.commit()
    return

# --- Endpoints para Comentarios ---

@router.post("/activities/{activity_id}/comments", response_model=models.Comment, status_code=status.HTTP_201_CREATED)
def create_comment_for_activity(
    activity_id: int, 
    comment: models.CommentCreate, 
    db: Session = Depends(database.get_db),
    current_user_id: int = Depends(auth.get_current_user_id)
):
    """
    Crea un nuevo comentario para una actividad específica.
    El autor se obtiene del token de autenticación.
    """
    db_activity = db.query(models.ActivityDB).filter(models.ActivityDB.id == activity_id).first()
    if db_activity is None:
        raise HTTPException(status_code=404, detail="Activity not found")

    db_comment = models.CommentDB(**comment.dict(), activity_id=activity_id, author_id=current_user_id)
    db.add(db_comment)
    db.commit()
    db.refresh(db_comment)
    return db_comment

@router.get("/activities/{activity_id}/comments", response_model=List[models.Comment])
def read_comments_for_activity(activity_id: int, db: Session = Depends(database.get_db)):
    """Obtiene todos los comentarios de una actividad específica."""
    # Si se quisiera cargar la actividad junto con los comentarios, se usaría .options(joinedload(models.CommentDB.activity))
    # Pero el modelo Pydantic Comment no expone los detalles de la actividad, así que no es necesario aquí.
    comments = db.query(models.CommentDB).filter(models.CommentDB.activity_id == activity_id).order_by(models.CommentDB.created_at.desc()).all() # Ordenar por fecha
    
    # Obtener IDs de autores de comentarios únicos
    comment_author_ids = list(set(comment.author_id for comment in comments))
    comment_users_data = {}
    if comment_author_ids:
        try:
            for author_id in comment_author_ids:
                user_response = requests.get(f"{USERS_SVC_URL}/api/v1/users/{author_id}")
                user_response.raise_for_status()
                comment_users_data[author_id] = user_response.json().get("username", f"Usuario {author_id}")
        except requests.exceptions.RequestException:
            pass

    # Enriquecer los comentarios con el nombre del autor
    enriched_comments = []
    for comment in comments:
        comment_data = models.Comment.from_orm(comment).dict()
        comment_data["author_name"] = comment_users_data.get(comment.author_id, f"Usuario {comment.author_id}")
        enriched_comments.append(comment_data)
        
    return enriched_comments

# Endpoint para eliminar una actividad
@router.delete("/activities/{activity_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_activity(
    activity_id: int, 
    db: Session = Depends(database.get_db),
    current_user_id: int = Depends(auth.get_current_user_id)
):
    """
    Elimina una actividad de la base de datos por su ID.
    Solo el autor original puede eliminar su actividad.
    """
    db_activity = db.query(models.ActivityDB).filter(models.ActivityDB.id == activity_id).first()
    if db_activity is None:
        raise HTTPException(status_code=404, detail="Activity not found")
    if db_activity.author_id != current_user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to delete this activity")

    db.delete(db_activity)
    db.commit() # Gracias a `cascade="all, delete-orphan"`, los comentarios y likes asociados también se eliminan.
    return

# Función auxiliar para enriquecer la actividad con el nombre del autor y el estado del like
def _enrich_activity_with_user_data(db: Session, db_activity: models.ActivityDB, users_data: dict, token: Optional[str]):
    activity_data = models.Activity.from_orm(db_activity).dict()
    
    # Obtener nombre del autor
    author_id = db_activity.author_id
    if author_id in users_data:
        activity_data["author_name"] = users_data[author_id]
    else:
        try:
            user_response = requests.get(f"{USERS_SVC_URL}/api/v1/users/{author_id}")
            user_response.raise_for_status()
            activity_data["author_name"] = user_response.json().get("username", f"Usuario {author_id}")
        except requests.exceptions.RequestException:
            activity_data["author_name"] = f"Usuario {author_id}" # Fallback si el servicio de usuarios falla

    # Verificar si el usuario actual ha dado "Me gusta"
    activity_data["current_user_has_liked"] = False
    if token:
        try:
            current_user_id = auth.get_current_user_id(token)
            like = db.query(models.LikeDB).filter_by(activity_id=db_activity.id, user_id=current_user_id).first()
            activity_data["current_user_has_liked"] = like is not None
        except HTTPException:
            pass # Si el token es inválido, simplemente no marcamos el "like"
            
    return activity_data

# Incluye el router en la aplicación principal con un prefijo
app.include_router(router, prefix="/api/v1")
    db: Session = Depends(database.get_db),
    current_user_id: int = Depends(auth.get_current_user_id)
):
    """
    Elimina una actividad de la base de datos por su ID.
    Solo el autor original puede eliminar su actividad.
    """
    db_activity = db.query(models.ActivityDB).filter(models.ActivityDB.id == activity_id).first()
    if db_activity is None:
        raise HTTPException(status_code=404, detail="Activity not found")
    if db_activity.author_id != current_user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to delete this activity")

    db.delete(db_activity)
    db.commit() # Gracias a `cascade="all, delete-orphan"`, los comentarios y likes asociados también se eliminan.
    return

# Incluye el router en la aplicación principal con un prefijo
app.include_router(router, prefix="/api/v1")
