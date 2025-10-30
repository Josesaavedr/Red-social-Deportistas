from fastapi import FastAPI, APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session # , joinedload # Importar joinedload si se van a cargar relaciones anidadas
from typing import List, Optional
from fastapi.security import OAuth2PasswordBearer

# Importa los módulos de base de datos y modelos
from . import models, database, auth, repository, config
from common.helpers.utils import send_async_bulk_request

app = FastAPI()

# La creación de tablas ahora se gestiona con Alembic.
# @app.on_event("startup")
# def on_startup():
#     models.Base.metadata.create_all(bind=database.engine)

# Crea una instancia del router para organizar los endpoints
router = APIRouter()
# Esquema para autenticación opcional (para saber si un usuario ha dado like)
oauth2_scheme_optional = OAuth2PasswordBearer(tokenUrl="token", auto_error=False)


@app.get("/")
def read_root():
    return {"message": "Servicio de Actividades en funcionamiento."}

@app.get("/health")
def health_check():
    """Endpoint de salud para verificar el estado del servicio."""
    return {"status": "ok"}

# Endpoint para obtener todas las actividades
@router.get("/activities/", response_model=List[models.Activity])
async def read_activities(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(database.get_db),
    token: Optional[str] = Depends(oauth2_scheme_optional)
):
    """
    Obtiene una lista de actividades, enriquecida con nombres de autor.
    """
    activities_db = repository.get_activities(db, skip=skip, limit=limit)
    
    # 1. Recolectar IDs de autores
    author_ids = list(set(act.author_id for act in activities_db))
    
    # 2. Obtener datos de usuarios en lote
    users_map = await send_async_bulk_request(f"{config.settings.USERS_SVC_URL}/api/v1/users/bulk", author_ids)

    # 3. Enriquecer y devolver actividades
    enriched_activities = []
    for activity_db in activities_db:
        enriched_activity = _enrich_activity_data(db, activity_db, users_map, token)
        enriched_activities.append(enriched_activity)
        
    return enriched_activities

# Endpoint para contar el total de actividades
@router.get("/activities/count")
def count_activities(db: Session = Depends(database.get_db)):
    """
    Cuenta el número total de actividades en la base de datos.
    """
    return {"total": repository.count_activities(db)}

# Endpoint para obtener una actividad específica por su ID
@router.get("/activities/{activity_id}", response_model=models.Activity)
async def read_activity(
    activity_id: int, 
    db: Session = Depends(database.get_db),
    token: Optional[str] = Depends(oauth2_scheme_optional)
):
    """
    Obtiene los detalles de una actividad, enriquecida con el nombre del autor
    y si el usuario actual le ha dado "like".
    """
    activity_db = repository.get_activity_by_id(db, activity_id=activity_id)
    
    # Obtener datos del autor
    users_map = await send_async_bulk_request(f"{config.settings.USERS_SVC_URL}/api/v1/users/bulk", [activity_db.author_id])

    return _enrich_activity_data(db, activity_db, users_map, token)
    
# Endpoint para crear una nueva actividad
@router.post("/activities/", response_model=models.Activity, status_code=status.HTTP_201_CREATED)
async def create_activity(
    activity: models.ActivityCreate, 
    db: Session = Depends(database.get_db),
    current_user_id: int = Depends(auth.get_current_user_id)
):
    """
    Crea una nueva actividad, la guarda y devuelve el objeto enriquecido.
    """
    activity_db = repository.create_activity(db, activity=activity, author_id=current_user_id)
    
    # Enriquecer la respuesta con el nombre del autor
    users_map = await send_async_bulk_request(f"{config.settings.USERS_SVC_URL}/api/v1/users/bulk", [activity_db.author_id])
    
    # No se necesita token para el estado de 'like', ya que es una actividad nueva
    return _enrich_activity_data(db, activity_db, users_map, token=None)

# Endpoint para actualizar una actividad
@router.put("/activities/{activity_id}", response_model=models.Activity)
async def update_activity(
    activity_id: int, 
    activity: models.ActivityUpdate, 
    db: Session = Depends(database.get_db),
    current_user_id: int = Depends(auth.get_current_user_id)
):
    """
    Actualiza una actividad existente y devuelve el objeto enriquecido.
    Solo el autor original puede actualizar su actividad.
    """
    activity_db = repository.update_activity(db, activity_id=activity_id, activity_update=activity, current_user_id=current_user_id)
    
    # Enriquecer la respuesta con el nombre del autor
    users_map = await send_async_bulk_request(f"{config.settings.USERS_SVC_URL}/api/v1/users/bulk", [activity_db.author_id])
    
    # No se necesita token para el estado de 'like' en la actualización
    return _enrich_activity_data(db, activity_db, users_map, token=None)

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
    return repository.create_like(db, activity_id=activity_id, user_id=current_user_id)

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
    return repository.delete_like(db, activity_id=activity_id, user_id=current_user_id)

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
    return repository.create_comment(db, activity_id=activity_id, comment=comment, author_id=current_user_id)

@router.get("/activities/{activity_id}/comments", response_model=List[models.Comment])
async def read_comments_for_activity(activity_id: int, db: Session = Depends(database.get_db)):
    """Obtiene todos los comentarios de una actividad, enriquecidos con el nombre del autor."""
    comments_db = repository.get_comments_for_activity(db, activity_id=activity_id)

    # 1. Recolectar IDs de autores de comentarios
    author_ids = list(set(comment.author_id for comment in comments_db))

    # 2. Obtener datos de usuarios en lote
    users_map = await send_async_bulk_request(f"{config.settings.USERS_SVC_URL}/api/v1/users/bulk", author_ids)

    # 3. Enriquecer comentarios
    enriched_comments = []
    for comment_db in comments_db:
        comment_data = models.Comment.from_orm(comment_db)
        author_info = users_map.get(comment_db.author_id)
        comment_data.author_name = author_info.get("username") if author_info else f"Usuario {comment_db.author_id}"
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
    repository.delete_activity(db, activity_id=activity_id, current_user_id=current_user_id)
    return

# --- Funciones Auxiliares ---

def _enrich_activity_data(db: Session, activity_db: models.ActivityDB, users_map: dict, token: Optional[str]) -> models.Activity:
    """Función auxiliar para añadir datos de usuario y estado de 'like' a una actividad."""
    activity_data = models.Activity.from_orm(activity_db)

    # 1. Añadir nombre de autor
    author_info = users_map.get(activity_db.author_id)
    activity_data.author_name = author_info.get("username") if author_info else f"Usuario {activity_db.author_id}"

    # 2. Comprobar si el usuario actual ha dado "like"
    activity_data.current_user_has_liked = False
    if token:
        try:
            # Decodificamos el token para obtener el ID del usuario actual
            current_user_id = auth.get_current_user_id(token)
            # Buscamos si existe un 'like' de este usuario para esta actividad
            like = db.query(models.LikeDB).filter_by(activity_id=activity_db.id, user_id=current_user_id).first()
            activity_data.current_user_has_liked = like is not None
        except HTTPException:
            # Si el token es inválido o no se proporciona, se asume que no hay 'like'
            pass
            
    return activity_data

# Incluye el router en la aplicación principal con un prefijo
app.include_router(router, prefix="/api/v1")
