# /services/actividades/config.py

import os
from pydantic import BaseSettings

class Settings(BaseSettings):
    # URL del servicio de usuarios, con un valor por defecto para desarrollo local
    USERS_SVC_URL: str = os.getenv("USERS_SVC_URL", "http://localhost:8001")

# Crea una instancia global de la configuración
settings = Settings()