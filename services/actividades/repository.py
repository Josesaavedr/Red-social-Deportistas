# /services/actividades/repository.py

from sqlalchemy.orm import Session
from typing import List, Optional
from fastapi import HTTPException, status

from . import models


def get_activity_by_id(db: Session, activity_id: int) -> models.ActivityDB:
    """
    Obtiene una actividad por su ID. Lanza un error 404 si no se encuentra.
    """
    db_activity = db.query(models.ActivityDB).filter(models.ActivityDB.id == activity_id).first()
    if db_activity is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Activity not found")
    return db_activity


def get_activities(db: Session, skip: int = 0, limit: int = 100) -> List[models.ActivityDB]:
    """
    Obtiene una lista paginada de actividades.
    """
    return db.query(models.ActivityDB).offset(skip).limit(limit).all()


def count_activities(db: Session) -> int:
    """
    Cuenta el número total de actividades.
    """
    return db.query(models.ActivityDB).count()


def create_activity(db: Session, activity: models.ActivityCreate, author_id: int) -> models.ActivityDB:
    """
    Crea una nueva actividad en la base de datos.
    """
    db_activity = models.ActivityDB(**activity.dict(), author_id=author_id)
    db.add(db_activity)
    db.commit()
    db.refresh(db_activity)
    return db_activity


def update_activity(db: Session, activity_id: int, activity_update: models.ActivityUpdate, current_user_id: int) -> models.ActivityDB:
    """
    Actualiza una actividad existente, verificando la autorización del autor.
    """
    db_activity = get_activity_by_id(db, activity_id)
    if db_activity.author_id != current_user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to update this activity")

    update_data = activity_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_activity, key, value)

    db.commit()
    db.refresh(db_activity)
    return db_activity


def delete_activity(db: Session, activity_id: int, current_user_id: int):
    """
    Elimina una actividad, verificando la autorización del autor.
    """
    db_activity = get_activity_by_id(db, activity_id)
    if db_activity.author_id != current_user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to delete this activity")

    db.delete(db_activity)
    db.commit()


def create_like(db: Session, activity_id: int, user_id: int) -> models.LikeDB:
    """
    Crea un 'like' para una actividad, evitando duplicados.
    """
    # 1. Verificar si la actividad existe
    db_activity = get_activity_by_id(db, activity_id)

    # 2. Verificar si ya existe un 'like'
    existing_like = db.query(models.LikeDB).filter(
        models.LikeDB.activity_id == activity_id,
        models.LikeDB.user_id == user_id
    ).first()

    if existing_like:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User already liked this activity")

    # 3. Crear el 'like' y actualizar contador
    db_like = models.LikeDB(activity_id=activity_id, user_id=user_id)
    db.add(db_like)
    db_activity.likes += 1

    db.commit()
    db.refresh(db_like)
    return db_like

def delete_like(db: Session, activity_id: int, user_id: int):
    """
    Elimina un 'like' de una actividad, actualizando el contador.
    """
    # 1. Verificar si la actividad existe para evitar condiciones de carrera
    db_activity = get_activity_by_id(db, activity_id)

    # 2. Encontrar el 'like' a eliminar
    db_like = db.query(models.LikeDB).filter(
        models.LikeDB.activity_id == activity_id,
        models.LikeDB.user_id == user_id
    ).first()

    if db_like is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Like not found for this activity and user")

    # 3. Eliminar el 'like' y decrementar el contador
    db.delete(db_like)
    if db_activity.likes > 0:
        db_activity.likes -= 1

    db.commit()

def create_comment(db: Session, activity_id: int, comment: models.CommentCreate, author_id: int) -> models.CommentDB:
    """
    Crea un nuevo comentario para una actividad.
    """
    # Verificar que la actividad existe
    get_activity_by_id(db, activity_id)

    db_comment = models.CommentDB(**comment.dict(), activity_id=activity_id, author_id=author_id)
    db.add(db_comment)
    db.commit()
    db.refresh(db_comment)
    return db_comment

def get_comments_for_activity(db: Session, activity_id: int) -> List[models.CommentDB]:
    """
    Obtiene todos los comentarios para una actividad específica.
    """
    # Verificar que la actividad existe
    get_activity_by_id(db, activity_id)
    
    return db.query(models.CommentDB).filter(models.CommentDB.activity_id == activity_id).order_by(models.CommentDB.created_at.desc()).all()