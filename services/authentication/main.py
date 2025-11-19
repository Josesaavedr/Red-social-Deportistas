from fastapi import FastAPI, APIRouter, HTTPException
import os

app = FastAPI(title="Authentication Service")

router = APIRouter()

@app.get("/")
def read_root():
    return {"message": "Servicio de Autenticación en funcionamiento."}

@app.get("/health")
def health_check():
    """Endpoint de salud para verificar el estado del servicio."""
    return {"status": "ok", "service": "authentication"}

# Endpoints de ejemplo para autenticación
@router.post("/login")
async def login(credentials: dict):
    """Iniciar sesión."""
    return {"message": "Login exitoso", "token": "example_token"}

@router.post("/register")
async def register(user_data: dict):
    """Registrar un nuevo usuario."""
    return {"message": "Usuario registrado exitosamente", "data": user_data}

@router.post("/logout")
async def logout():
    """Cerrar sesión."""
    return {"message": "Logout exitoso"}

@router.get("/verify")
async def verify_token(token: str):
    """Verificar un token."""
    return {"message": "Token válido", "token": token}

app.include_router(router, prefix="/api/v1")
