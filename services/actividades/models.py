# /services/actividades/models.py

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, UniqueConstraint, Boolean
from sqlalchemy.sql import func
from pydantic import BaseModel
from datetime import datetime
from typing import Optional

# Importa la base declarativa desde el archivo de configuración de la base de datos.
from .database import Base 

# Importa 'relationship' para definir las relaciones entre modelos
from sqlalchemy.orm import relationship

# Modelo de SQLAlchemy para la tabla 'activities' en la base de datos
class ActivityDB(Base):
    __tablename__ = "activities"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True, nullable=False) # Título de la actividad, no puede ser nulo
    content = Column(String, nullable=False) # Contenido/descripción de la actividad, no puede ser nulo
    author_id = Column(Integer, index=True, nullable=False) # ID del autor de la actividad (desde el servicio de usuarios)
    likes = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relaciones con otros modelos
    comments = relationship("CommentDB", back_populates="activity", cascade="all, delete-orphan")
    likers = relationship("LikeDB", back_populates="activity", cascade="all, delete-orphan")

# --- Modelos Pydantic para la validación de datos de la API ---

# Modelo base con los campos comunes
class ActivityBase(BaseModel):
    """Modelo base para actividades, define los campos comunes."""
    title: str
    content: str

# Modelo para la creación de una actividad (lo que se recibe en el POST)
class ActivityCreate(ActivityBase):
    """Modelo para crear una nueva actividad."""

# Modelo para actualizar una actividad (lo que se recibe en el PUT)
# Todos los campos son opcionales.
class ActivityUpdate(BaseModel):
    """Modelo para actualizar parcialmente una actividad."""
    title: Optional[str] = None
    content: Optional[str] = None

# Modelo para leer/retornar una actividad (incluye campos generados por la BD)
class Activity(ActivityBase):
    """Modelo para leer una actividad, incluyendo campos generados por la base de datos."""
    author_id: int
    id: int
    created_at: datetime
    likes: int
    # Campos enriquecidos que se añadirán antes de enviar la respuesta
    author_name: Optional[str] = None
    current_user_has_liked: Optional[bool] = False

    class Config:
        orm_mode = True # Permite que Pydantic lea datos desde modelos de SQLAlchemy
        # Para evitar problemas de referencia circular si se incluyen relaciones anidadas
        # Se puede usar update_forward_refs() después de definir todos los modelos

# --- Modelos para Comentarios ---

# Modelo de SQLAlchemy para la tabla 'comments'
class CommentDB(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, index=True)
    content = Column(String, nullable=False) # Contenido del comentario
    author_id = Column(Integer, index=True, nullable=False) # ID del autor del comentario
    activity_id = Column(Integer, ForeignKey("activities.id"), index=True, nullable=False) # ID de la actividad a la que pertenece el comentario
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relación con el modelo ActivityDB
    activity = relationship("ActivityDB", back_populates="comments")

# Modelo Pydantic para la creación de un comentario
class CommentCreate(BaseModel):
    """Modelo para crear un nuevo comentario."""
    content: str

# Modelo Pydantic para leer/retornar un comentario
class Comment(CommentCreate):
    """Modelo para leer un comentario, incluyendo campos generados por la base de datos."""
    id: int
    created_at: datetime
    activity_id: int
    author_id: int
    # Campo enriquecido
    author_name: Optional[str] = None

    class Config:
        orm_mode = True

# --- Modelos para Likes ---

# Modelo de SQLAlchemy para la tabla 'likes'
class LikeDB(Base):
    __tablename__ = "likes"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True, nullable=False) # ID del usuario que dio "me gusta"
    activity_id = Column(Integer, ForeignKey("activities.id"), index=True, nullable=False) # ID de la actividad a la que se dio "me gusta"
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (UniqueConstraint('user_id', 'activity_id', name='_user_activity_uc'),)

    # Relación con el modelo ActivityDB
    activity = relationship("ActivityDB", back_populates="likers")

# Modelo Pydantic para la creación de un "Me gusta"
class LikeCreate(BaseModel):
    """Modelo para crear un nuevo "me gusta"."""
    pass # No necesita campos, el user_id vendrá del token

# Modelo Pydantic para leer/retornar un "Me gusta"
class Like(BaseModel):
    """Modelo para leer un "me gusta", incluyendo campos generados por la base de datos."""
    id: int
    created_at: datetime
    activity_id: int
    user_id: int

    class Config:
        orm_mode = True