from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from datetime import datetime

from pydantic import BaseModel
from typing import Optional

# Define la base declarativa
from .database import Base

# --- Modelos de SQLAlchemy ---

class PostDB(Base):
    __tablename__ = "posts"
    id = Column(Integer, primary_key=True, index=True)
    content = Column(String, nullable=False)
    author_id = Column(Integer, index=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class FollowerDB(Base):
    __tablename__ = "followers"
    id = Column(Integer, primary_key=True, index=True)
    # El usuario que sigue a otro
    follower_id = Column(Integer, index=True, nullable=False)
    # El usuario que es seguido
    followed_id = Column(Integer, index=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (UniqueConstraint('follower_id', 'followed_id', name='_follower_followed_uc'),)

# --- Modelos Pydantic ---

# Modelos para Posts
class PostBase(BaseModel):
    content: str
    
class PostCreate(PostBase):
    pass

class Post(PostBase):
    id: int
    author_id: int
    created_at: datetime
    author_name: Optional[str] = None # Se enriquecerá con datos del servicio de usuarios
    
    class Config:
        orm_mode = True

# Modelos para Seguidores
class Follower(BaseModel):
    follower_id: int
    followed_id: int
    created_at: datetime

    class Config:
        orm_mode = True
