from fastapi import FastAPI, APIRouter, HTTPException
import os

app = FastAPI(title="Notifications Service")

router = APIRouter()

@app.get("/")
def read_root():
    return {"message": "Servicio de Notificaciones en funcionamiento."}

@app.get("/health")
def health_check():
    """Endpoint de salud para verificar el estado del servicio."""
    return {"status": "ok", "service": "notifications"}

# Endpoints de ejemplo para notificaciones
@router.get("/notificaciones")
async def get_notificaciones():
    """Obtener lista de notificaciones."""
    return {"data": [], "message": "Lista de notificaciones"}

@router.post("/notificaciones")
async def create_notificacion(notificacion: dict):
    """Crear una nueva notificación."""
    return {"message": "Notificación creada exitosamente", "data": notificacion}

@router.post("/enviar")
async def enviar_notificacion(notificacion: dict):
    """Enviar una notificación."""
    return {"message": "Notificación enviada exitosamente", "data": notificacion}

app.include_router(router)
