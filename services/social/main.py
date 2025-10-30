from fastapi import FastAPI, APIRouter, HTTPException, Depends, status
import os
from typing import List, Optional
from sqlalchemy.orm import Session
import requests

# Importar los módulos de base de datos, modelos y autenticación
from . import database, models, auth, repository

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
    """Crea una nueva publicación (post) para el usuario autenticado."""
    return repository.create_post(db, post=post, author_id=current_user_id)

@router.get("/posts/feed/", response_model=List[models.Post])
def get_user_feed(
    db: Session = Depends(database.get_db),
    current_user_id: int = Depends(auth.get_current_user_id)
):
    """Obtiene las publicaciones de los usuarios que el usuario actual sigue."""
    return repository.get_user_feed(db, user_id=current_user_id)

@router.get("/users/{user_id}/posts/", response_model=List[models.Post])
def get_user_posts(user_id: int, db: Session = Depends(database.get_db)):
    """Obtiene todas las publicaciones de un usuario específico."""
    return repository.get_user_posts(db, user_id=user_id)

# --- Endpoints para Seguidores (Followers) ---

@router.post("/users/{user_id}/follow", status_code=status.HTTP_204_NO_CONTENT)
def follow_user(
    user_id: int,
    db: Session = Depends(database.get_db),
    current_user_id: int = Depends(auth.get_current_user_id)
):
    """Permite al usuario actual seguir a otro usuario."""
    repository.follow_user(db, follower_id=current_user_id, followed_id=user_id)
    return

@router.delete("/users/{user_id}/follow", status_code=status.HTTP_204_NO_CONTENT)
def unfollow_user(
    user_id: int,
    db: Session = Depends(database.get_db),
    current_user_id: int = Depends(auth.get_current_user_id)
):
    """Permite al usuario actual dejar de seguir a otro usuario."""
    repository.unfollow_user(db, follower_id=current_user_id, followed_id=user_id)
    return

@router.get("/users/{user_id}/followers", response_model=List[int])
def get_followers(user_id: int, db: Session = Depends(database.get_db)):
    """Obtiene la lista de IDs de los seguidores de un usuario."""
    return repository.get_followers(db, user_id=user_id)

@router.get("/users/{user_id}/following", response_model=List[int])
def get_following(user_id: int, db: Session = Depends(database.get_db)):
    """Obtiene la lista de IDs de los usuarios que un usuario sigue."""
    return repository.get_following(db, user_id=user_id)

app.include_router(router, prefix="/api/v1")

@app.on_event("startup")
def on_startup():
    # Esto es útil para desarrollo rápido. En producción, usa Alembic para migraciones.
    database.Base.metadata.create_all(bind=database.engine)
