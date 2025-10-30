from fastapi import FastAPI, APIRouter, HTTPException, Depends, status
import os
from typing import List, Optional
from sqlalchemy.orm import Session
import requests

# Importar los módulos de base de datos, modelos y autenticación
from . import database, models, auth

# URL del servicio de usuarios (obtenida de variables de entorno)
USERS_SVC_URL = os.getenv("USERS_SVC", "http://users:8001")

app = FastAPI()

# Crea una instancia del router para organizar los endpoints
router = APIRouter()

# Endpoint raíz
@app.get("/")
def read_root():
    return {"message": "Servicio Social en funcionamiento."}

@app.get("/health")
def health_check():
    """Endpoint de salud para verificar el estado del servicio."""
    return {"status": "ok"}

# --- Endpoints para Posts ---

@router.post("/posts/", response_model=models.Post, status_code=status.HTTP_201_CREATED)
def create_post(
    post: models.PostCreate,
    db: Session = Depends(database.get_db),
    current_user_id: int = Depends(auth.get_current_user_id)
):
    """Crea una nueva publicación (post)."""
    db_post = models.PostDB(**post.dict(), author_id=current_user_id)
    db.add(db_post)
    db.commit()
    db.refresh(db_post)
    return db_post

@router.get("/posts/feed/", response_model=List[models.Post])
def get_user_feed(
    db: Session = Depends(database.get_db),
    current_user_id: int = Depends(auth.get_current_user_id)
):
    """Obtiene las publicaciones de los usuarios que el usuario actual sigue."""
    followed_users = db.query(models.FollowerDB.followed_id).filter(models.FollowerDB.follower_id == current_user_id).all()
    followed_user_ids = [user.followed_id for user in followed_users]

    # Incluir también los posts del propio usuario en su feed
    followed_user_ids.append(current_user_id)

    posts = db.query(models.PostDB).filter(models.PostDB.author_id.in_(followed_user_ids)).order_by(models.PostDB.created_at.desc()).limit(100).all()
    return posts

@router.get("/users/{user_id}/posts/", response_model=List[models.Post])
def get_user_posts(user_id: int, db: Session = Depends(database.get_db)):
    """Obtiene todas las publicaciones de un usuario específico."""
    posts = db.query(models.PostDB).filter(models.PostDB.author_id == user_id).order_by(models.PostDB.created_at.desc()).all()
    return posts

# --- Endpoints para Seguidores (Followers) ---

@router.post("/users/{user_id}/follow", status_code=status.HTTP_204_NO_CONTENT)
def follow_user(
    user_id: int,
    db: Session = Depends(database.get_db),
    current_user_id: int = Depends(auth.get_current_user_id)
):
    """Permite al usuario actual seguir a otro usuario."""
    if user_id == current_user_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="You cannot follow yourself")

    # Verificar si ya lo sigue
    existing_follow = db.query(models.FollowerDB).filter_by(follower_id=current_user_id, followed_id=user_id).first()
    if existing_follow:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="You are already following this user")

    # TODO: Verificar que el user_id a seguir existe llamando al servicio de usuarios

    db_follow = models.FollowerDB(follower_id=current_user_id, followed_id=user_id)
    db.add(db_follow)
    db.commit()
    return

@router.delete("/users/{user_id}/follow", status_code=status.HTTP_204_NO_CONTENT)
def unfollow_user(
    user_id: int,
    db: Session = Depends(database.get_db),
    current_user_id: int = Depends(auth.get_current_user_id)
):
    """Permite al usuario actual dejar de seguir a otro usuario."""
    db_follow = db.query(models.FollowerDB).filter_by(follower_id=current_user_id, followed_id=user_id).first()
    if not db_follow:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="You are not following this user")

    db.delete(db_follow)
    db.commit()
    return

@router.get("/users/{user_id}/followers", response_model=List[int])
def get_followers(user_id: int, db: Session = Depends(database.get_db)):
    """Obtiene la lista de IDs de los seguidores de un usuario."""
    followers = db.query(models.FollowerDB.follower_id).filter(models.FollowerDB.followed_id == user_id).all()
    return [f.follower_id for f in followers]

@router.get("/users/{user_id}/following", response_model=List[int])
def get_following(user_id: int, db: Session = Depends(database.get_db)):
    """Obtiene la lista de IDs de los usuarios que un usuario sigue."""
    following = db.query(models.FollowerDB.followed_id).filter(models.FollowerDB.follower_id == user_id).all()
    return [f.followed_id for f in following]

app.include_router(router, prefix="/api/v1")

@app.on_event("startup")
def on_startup():
    # Esto es útil para desarrollo rápido. En producción, usa Alembic para migraciones.
    database.Base.metadata.create_all(bind=database.engine)
