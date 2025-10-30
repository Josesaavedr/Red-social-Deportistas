# /services/social/repository.py

from sqlalchemy.orm import Session
from typing import List
from fastapi import HTTPException, status

from . import models


def create_post(db: Session, post: models.PostCreate, author_id: int) -> models.PostDB:
    """
    Crea una nueva publicación (post) en la base de datos.
    """
    db_post = models.PostDB(**post.dict(), author_id=author_id)
    db.add(db_post)
    db.commit()
    db.refresh(db_post)
    return db_post


def get_user_feed(db: Session, user_id: int, limit: int = 100) -> List[models.PostDB]:
    """
    Obtiene las publicaciones de los usuarios que el usuario actual sigue,
    incluyendo las publicaciones del propio usuario.
    """
    followed_users = db.query(models.FollowerDB.followed_id).filter(models.FollowerDB.follower_id == user_id).all()
    followed_user_ids = [user.followed_id for user in followed_users]

    # Incluir también los posts del propio usuario en su feed
    followed_user_ids.append(user_id)

    posts = (
        db.query(models.PostDB)
        .filter(models.PostDB.author_id.in_(followed_user_ids))
        .order_by(models.PostDB.created_at.desc())
        .limit(limit)
        .all()
    )
    return posts


def get_user_posts(db: Session, user_id: int) -> List[models.PostDB]:
    """
    Obtiene todas las publicaciones de un usuario específico.
    """
    return db.query(models.PostDB).filter(models.PostDB.author_id == user_id).order_by(models.PostDB.created_at.desc()).all()


def follow_user(db: Session, follower_id: int, followed_id: int):
    """
    Crea una relación de seguimiento entre dos usuarios.
    """
    if followed_id == follower_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="You cannot follow yourself")

    # Verificar si ya lo sigue
    existing_follow = db.query(models.FollowerDB).filter_by(follower_id=follower_id, followed_id=followed_id).first()
    if existing_follow:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="You are already following this user")

    # TODO: Verificar que el `followed_id` a seguir existe llamando al servicio de autenticación.
    # Esto evitaría relaciones de seguimiento a usuarios inexistentes.

    db_follow = models.FollowerDB(follower_id=follower_id, followed_id=followed_id)
    db.add(db_follow)
    db.commit()


def unfollow_user(db: Session, follower_id: int, followed_id: int):
    """
    Elimina una relación de seguimiento.
    """
    db_follow = db.query(models.FollowerDB).filter_by(follower_id=follower_id, followed_id=followed_id).first()
    if not db_follow:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="You are not following this user")

    db.delete(db_follow)
    db.commit()


def get_followers(db: Session, user_id: int) -> List[int]:
    """
    Obtiene la lista de IDs de los seguidores de un usuario.
    """
    followers = db.query(models.FollowerDB.follower_id).filter(models.FollowerDB.followed_id == user_id).all()
    return [f.follower_id for f in followers]


def get_following(db: Session, user_id: int) -> List[int]:
    """
    Obtiene la lista de IDs de los usuarios que un usuario sigue.
    """
    following = db.query(models.FollowerDB.followed_id).filter(models.FollowerDB.follower_id == user_id).all()
    return [f.followed_id for f in following]