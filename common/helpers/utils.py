import json
import requests
import httpx
import logging
from typing import Any
from datetime import datetime

# Configure logger
logger = logging.getLogger(__name__)

# TODO: Define funciones de ayuda que puedan ser útiles en varios microservicios.

def send_request_to_service(url: str, method: str = "GET", data: Any = None):
    """
    Envía una petición HTTP SÍNCRONA a otro microservicio.
    Útil para scripts o tareas en segundo plano que no son async.
    
    Args:
        url (str): La URL completa del endpoint.
        method (str): El método HTTP (GET, POST, PUT, DELETE).
        data (Any): Los datos a enviar en el cuerpo de la petición (para POST/PUT).
    
    Returns:
        dict: La respuesta del servicio en formato JSON.
    
    Raises:
        requests.exceptions.RequestException: Si la petición falla.
    """
    try:
        response = requests.request(method, url, json=data)
        response.raise_for_status()  # Lanza una excepción si la respuesta es un error
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"Error en la petición síncrona: {e}")
        raise e

async def send_async_request_to_service(url: str, method: str = "GET", data: Any = None):
    """
    Envía una petición HTTP ASÍNCRONA a otro microservicio.
    Ideal para usar dentro de endpoints de FastAPI.
    
    Args:
        url (str): La URL completa del endpoint.
        method (str): El método HTTP (GET, POST, PUT, DELETE).
        data (Any): Los datos a enviar en el cuerpo de la petición (para POST/PUT).
    
    Returns:
        dict: La respuesta del servicio en formato JSON.
    
    Raises:
        httpx.HTTPError: Si la petición falla.
    """
    async with httpx.AsyncClient() as client:
        try:
            response = await client.request(method, url, json=data)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            logger.error(f"Error en la petición asíncrona: {e}")
            raise e

def format_date(dt_object: datetime):
    """Formatea un objeto datetime a una cadena de texto."""
    if not isinstance(dt_object, datetime):
        return dt_object # Devuelve el valor original si no es un datetime
    return dt_object.strftime("%Y-%m-%d %H:%M:%S")

# TODO: Agrega más funciones de utilidad según sea necesario.

# ------------------------------------------------------------------------------
# Ejemplo de uso en un microservicio
# from common.helpers.utils import send_request_to_service
# from common.config import settings # Asumiendo que tienes un config.py
# 
# URL del servicio de autenticación
# auth_url = f"{settings.AUTH_SERVICE_URL}/users"
# 
# try:
#     # Envía una petición para obtener todos los usuarios del servicio de autenticación
#     users = await send_async_request_to_service(auth_url)
#     print("Usuarios obtenidos:", users)
# except httpx.HTTPError:
#     print("No se pudo obtener la lista de usuarios.")
#