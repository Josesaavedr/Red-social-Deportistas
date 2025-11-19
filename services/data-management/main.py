from fastapi import FastAPI, APIRouter, HTTPException
import os

app = FastAPI(title="Data Management Service")

router = APIRouter()

@app.get("/")
def read_root():
    return {"message": "Servicio de Gestión de Datos en funcionamiento."}

@app.get("/health")
def health_check():
    """Endpoint de salud para verificar el estado del servicio."""
    return {"status": "ok", "service": "data-management"}

# Endpoints de ejemplo para gestión de datos
@router.get("/deportistas")
async def get_deportistas():
    """Obtener lista de deportistas."""
    return {"data": [], "message": "Lista de deportistas"}

@router.post("/deportistas")
async def create_deportista(deportista: dict):
    """Crear un nuevo deportista."""
    return {"message": "Deportista creado exitosamente", "data": deportista}

@router.get("/estadisticas")
async def get_estadisticas():
    """Obtener estadísticas de deportistas."""
    return {"data": {}, "message": "Estadísticas de deportistas"}

app.include_router(router, prefix="/api/v1")
