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


@router.get("/deportistas")
async def get_deportistas():
    """Retorna publicaciones almacenadas por clientes externos (sin datos ficticios)."""
    return {"data": [], "message": "Publicaciones disponibles"}


@router.post("/deportistas")
async def create_deportista(deportista: dict):
    """Crear un nuevo registro (demo)."""
    return {"message": "Publicación registrada (demo)", "data": deportista}


@router.get("/estadisticas")
async def get_estadisticas():
    """Obtener estadísticas (vacías por defecto)."""
    return {"data": {"total_publicaciones": 0}, "message": "Estadísticas del feed"}


app.include_router(router)
