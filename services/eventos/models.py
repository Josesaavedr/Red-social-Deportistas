from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime

from pydantic import BaseModel
from typing import Optional

# Define la base declarativa
from .database import Base # Importa la Base desde database.py

# Modelo de SQLAlchemy para la tabla 'events' en la base de datos
class EventDB(Base):
    """
    Modelo de datos para un evento deportivo.
    """
    __tablename__ = "events"

    # Columnas de la tabla
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True, nullable=False)
    description = Column(String, nullable=True)
    location = Column(String, nullable=False)
    event_date = Column(DateTime, nullable=False) # Fecha y hora del evento
    organizer_id = Column(Integer, index=True, nullable=False) # ID del usuario organizador
    created_at = Column(DateTime, default=datetime.utcnow) # Fecha de creación del registro

    # Relaciones (si las hubiera, por ejemplo, con un servicio de usuarios)
    # organizer = relationship("UserDB", back_populates="events") # Si tuvieras un modelo UserDB

    def __repr__(self):
        return f"<Event(id={self.id}, title='{self.title}', date='{self.event_date}')>"

# --- Modelos Pydantic para la validación de datos de la API ---

class EventBase(BaseModel):
    """Modelo base para eventos, define los campos comunes."""
    title: str
    description: Optional[str] = None
    location: str
    event_date: datetime

class EventCreate(EventBase):
    """Modelo para crear un nuevo evento."""
    pass

class EventUpdate(BaseModel):
    """Modelo para actualizar parcialmente un evento."""
    title: Optional[str] = None
    description: Optional[str] = None
    location: Optional[str] = None
    event_date: Optional[datetime] = None

class Event(EventBase):
    """Modelo para leer un evento, incluyendo campos generados por la base de datos."""
    id: int
    organizer_id: int
    created_at: datetime
    
    class Config:
        orm_mode = True # Habilita la compatibilidad con ORM
