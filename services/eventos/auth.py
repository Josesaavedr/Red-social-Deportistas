# /services/eventos/auth.py

import os
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from pydantic import BaseModel

# Clave secreta para decodificar el JWT. Debe ser la misma que en el API Gateway.
JWT_SECRET = os.getenv("JWT_SECRET", "your_jwt_secret")
ALGORITHM = "HS256"

# Define el esquema de seguridad para la documentación de la API
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

class TokenData(BaseModel):
    """Modelo para los datos contenidos en el token."""
    user_id: int | None = None

def get_current_user_id(token: str = Depends(oauth2_scheme)) -> int:
    """
    Dependencia para validar el token JWT y obtener el ID del usuario.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[ALGORITHM])
        # El ID del usuario se espera en el campo 'sub' (subject) del token
        user_id: int = int(payload.get("sub"))
        if user_id is None:
            raise credentials_exception
        return user_id
    except (JWTError, ValueError, TypeError):
        raise credentials_exception