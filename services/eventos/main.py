from fastapi import FastAPI, APIRouter, HTTPException, Depends, status
import os
from typing import List, Optional
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordBearer

# Importar los módulos de base de datos, modelos y autenticación
from . import database, models, auth
# Importar helpers y configuración
from common.helpers.utils import send_async_bulk_request

# URL del servicio de usuarios (obtenida de variables de entorno)
USERS_SVC_URL = os.getenv("USERS_SVC_URL", "http://localhost:8001")

app = FastAPI()

# Esquema para autenticación opcional (útil si un endpoint puede ser accedido por no autenticados)
oauth2_scheme_optional = OAuth2PasswordBearer(tokenUrl="token", auto_error=False)

# Crea una instancia del router para organizar los endpoints
router = APIRouter()

# Endpoint raíz
@app.get("/")
def read_root():
    return {"message": "Servicio de Eventos en funcionamiento."}

@app.get("/health")
def health_check():
    """Endpoint de salud para verificar el estado del servicio."""
    return {"status": "ok"}

# --- Endpoints CRUD para Eventos ---

# Endpoint para crear un nuevo evento
@router.post("/events/", response_model=models.Event, status_code=status.HTTP_201_CREATED)
async def create_event(
    event: models.EventCreate,
    db: Session = Depends(database.get_db),
    current_user_id: int = Depends(auth.get_current_user_id) # Requiere autenticación
):
    """
    Crea un nuevo evento y devuelve el objeto enriquecido.
    El organizador del evento se obtiene del token de autenticación.
    """
    db_event = models.EventDB(**event.dict(), organizer_id=current_user_id)
    db.add(db_event)
    db.commit()
    db.refresh(db_event)

    # Enriquecer la respuesta con el nombre del organizador
    users_map = await send_async_bulk_request(f"{USERS_SVC_URL}/api/v1/users/bulk", [db_event.organizer_id])
    
    event_data = models.Event.from_orm(db_event)
    organizer_info = users_map.get(db_event.organizer_id)
    event_data.organizer_name = organizer_info.get("username") if organizer_info else f"Usuario {db_event.organizer_id}"

    return event_data

# Endpoint para obtener todos los eventos
@router.get("/events/", response_model=List[models.Event])
async def read_events(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(database.get_db)
):
    """
    Obtiene una lista de eventos, enriquecida con los nombres de los organizadores.
    """
    events_db = db.query(models.EventDB).offset(skip).limit(limit).all()
    
    # 1. Recolectar IDs de organizadores
    organizer_ids = list(set(event.organizer_id for event in events_db))

    # 2. Obtener datos de usuarios en lote
    users_map = await send_async_bulk_request(f"{USERS_SVC_URL}/api/v1/users/bulk", organizer_ids)

    # 3. Enriquecer y devolver eventos
    enriched_events = []
    for event_db in events_db:
        event_data = models.Event.from_orm(event_db)
        organizer_info = users_map.get(event_db.organizer_id)
        event_data.organizer_name = organizer_info.get("username") if organizer_info else f"Usuario {event_db.organizer_id}"
        enriched_events.append(event_data)
        
    return enriched_events

# Endpoint para obtener un evento específico por su ID
@router.get("/events/{event_id}", response_model=models.Event)
async def read_event(
    event_id: int,
    db: Session = Depends(database.get_db)
):
    """
    Obtiene los detalles de un evento, enriquecido con el nombre del organizador.
    """
    db_event = db.query(models.EventDB).filter(models.EventDB.id == event_id).first()
    if db_event is None:
        raise HTTPException(status_code=404, detail="Event not found")

    # Obtener datos del organizador
    users_map = await send_async_bulk_request(f"{USERS_SVC_URL}/api/v1/users/bulk", [db_event.organizer_id])
    
    # Enriquecer y devolver el evento
    event_data = models.Event.from_orm(db_event)
    organizer_info = users_map.get(db_event.organizer_id)
    event_data.organizer_name = organizer_info.get("username") if organizer_info else f"Usuario {db_event.organizer_id}"
    
    return event_data

# Endpoint para actualizar un evento
@router.put("/events/{event_id}", response_model=models.Event)
async def update_event(
    event_id: int,
    event: models.EventUpdate,
    db: Session = Depends(database.get_db),
    current_user_id: int = Depends(auth.get_current_user_id) # Requiere autenticación
):
    """
    Actualiza un evento existente y devuelve el objeto enriquecido.
    Solo el organizador original puede actualizar su evento.
    """
    db_event = db.query(models.EventDB).filter(models.EventDB.id == event_id).first()
    if db_event is None:
        raise HTTPException(status_code=404, detail="Event not found")
    
    # Autorización: solo el organizador puede actualizar
    if db_event.organizer_id != current_user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to update this event")

    # Obtiene los datos del modelo Pydantic que no son None
    update_data = event.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_event, key, value)
    
    db.commit()
    db.refresh(db_event)

    # Enriquecer la respuesta con el nombre del organizador
    users_map = await send_async_bulk_request(f"{USERS_SVC_URL}/api/v1/users/bulk", [db_event.organizer_id])
    
    event_data = models.Event.from_orm(db_event)
    organizer_info = users_map.get(db_event.organizer_id)
    event_data.organizer_name = organizer_info.get("username") if organizer_info else f"Usuario {db_event.organizer_id}"

    return event_data

# Endpoint para eliminar un evento
@router.delete("/events/{event_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_event(
    event_id: int,
    db: Session = Depends(database.get_db),
    current_user_id: int = Depends(auth.get_current_user_id) # Requiere autenticación
):
    """
    Elimina un evento de la base de datos por su ID.
    Solo el organizador original puede eliminar su evento.
    """
    db_event = db.query(models.EventDB).filter(models.EventDB.id == event_id).first()
    if db_event is None:
        raise HTTPException(status_code=404, detail="Event not found")
    
    # Autorización: solo el organizador puede eliminar
    if db_event.organizer_id != current_user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to delete this event")

    db.delete(db_event)
    db.commit()
    return

# Incluir el router en la aplicación principal
app.include_router(router, prefix="/api/v1")

# Opcional: Hook de inicio para crear tablas si no se usa Alembic (solo para desarrollo)
@app.on_event("startup")
def on_startup():
    # Esto es útil para desarrollo rápido. En producción, usa Alembic para migraciones.
    models.Base.metadata.create_all(bind=database.engine)


# TODO: Incluir el router en la aplicación principal
# app.include_router(router, prefix="/api/v1")
