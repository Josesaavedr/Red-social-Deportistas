from typing import Optional, Dict, Any
import os
import time
import logging

from fastapi import FastAPI, Request, HTTPException, Depends, Header, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
import httpx
import redis.asyncio as redis
import jwt

# --- Configuración básica ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("api-gateway")

USERS_SVC = os.getenv("USERS_SVC", "http://users:8001")
POSTS_SVC = os.getenv("POSTS_SVC", "http://posts:8002")
ACTIVITIES_SVC = os.getenv("ACTIVITIES_SVC", "http://activities:8003")
MESSAGES_SVC = os.getenv("MESSAGES_SVC", "http://messages:8004")
EVENTS_SVC = os.getenv("EVENTS_SVC", "http://events:8005")
SOCIAL_SVC = os.getenv("SOCIAL_SVC", "http://social:8006")

JWT_SECRET = os.getenv("JWT_SECRET", "changeme")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost:5000").split(",")

# --- Configuración de Rate Limiting con Redis ---
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
RATE_LIMIT_PER_MINUTE = int(os.getenv("RATE_LIMIT_PER_MINUTE", "100"))

# --- Definición de Rutas y Servicios ---
SERVICE_MAP = {
    "users": {"url": USERS_SVC, "public_paths": ["/token", "/register"]},
    "posts": {"url": POSTS_SVC},
    "activities": {"url": ACTIVITIES_SVC, "public_paths": ["/"]},
    "messages": {"url": MESSAGES_SVC},
    "events": {"url": EVENTS_SVC},
    "social": {"url": SOCIAL_SVC},
}

app = FastAPI(title="API Gateway - Red Social Deportistas", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Clientes y Conexiones ---

# Cliente Redis para Rate Limiting
redis_client = redis.from_url(REDIS_URL, encoding="utf-8", decode_responses=True)

# Cliente HTTP asíncrono compartido con reintentos y pool de conexiones
retries = httpx.Limits(max_keepalives=10, max_connections=100)
transport = httpx.AsyncHTTPTransport(retries=3) # Reintenta 3 veces en fallos de conexión
client = httpx.AsyncClient(transport=transport, timeout=httpx.Timeout(15.0, connect=5.0))

# ---------------------- Utilidades ----------------------

async def rate_limit_middleware(key: str) -> bool:
    """
    Implementación de Rate Limiting con Redis usando el algoritmo de ventana deslizante.
    """
    try:
        # Usamos un pipeline para ejecutar comandos de forma atómica
        p = redis_client.pipeline()
        # Clave única para el minuto actual
        current_minute_key = f"rate_limit:{key}:{int(time.time() / 60)}"
        p.incr(current_minute_key)
        p.expire(current_minute_key, 60) # La clave expira en 60 segundos
        count = (await p.execute())[0]
        return count <= RATE_LIMIT_PER_MINUTE
    except redis.RedisError as e:
        logger.error(f"Error de Redis en Rate Limiting: {e}")
        return True # Falla en modo abierto para no bloquear a los usuarios si Redis cae

def verify_jwt(token: str) -> Dict[str, Any]:
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

async def get_bearer_token(authorization: Optional[str] = Header(None)) -> Optional[str]:
    if not authorization:
        return None
    parts = authorization.split()
    if len(parts) == 2 and parts[0].lower() == "bearer":
        return parts[1]
    return None

def get_service_for_path(path: str) -> Optional[Dict[str, Any]]:
    """Determina el servicio y la ruta interna a partir de la ruta completa."""
    parts = path.strip("/").split("/", 1)
    service_prefix = parts[0]
    
    if service_prefix in SERVICE_MAP:
        service_config = SERVICE_MAP[service_prefix]
        internal_path = f"/{parts[1]}" if len(parts) > 1 else "/"
        return {
            "url": service_config["url"],
            "path": internal_path,
            "public_paths": service_config.get("public_paths", [])
        }
    return None

async def proxy_request(request: Request, service_url: str, path: str):
    """Reenvía la petición al microservicio destino y devuelve la respuesta"""
    url = f"{service_url}{path}"
    method = request.method
    body = request.stream()
    query_params = request.query_params
    
    # Copia cabeceras, eliminando las que no deben ser reenviadas (hop-by-hop)
    headers_to_forward = {
        k: v for k, v in request.headers.items() 
        if k.lower() not in ("host", "connection", "keep-alive", "proxy-authenticate", 
                             "proxy-authorization", "te", "trailer", "transfer-encoding", "upgrade")
    }

    try:
        # Construye y envía la petición al servicio destino
        req = client.build_request(method, url, headers=headers_to_forward, content=body, params=query_params)
        resp = await client.send(req, stream=True)
        
        # Devuelve la respuesta en streaming para mayor eficiencia
        return StreamingResponse(resp.aiter_bytes(), status_code=resp.status_code, headers=resp.headers)
    except httpx.HTTPError as e:
        logger.error(f"Error al contactar el servicio {url}: {e}")
        raise HTTPException(status_code=502, detail=f"Error al contactar el servicio: {e.__class__.__name__}")

# ---------------------- Endpoints ----------------------

@app.middleware("http")
async def add_logging_and_rate_limit(request: Request, call_next):
    start = time.time()
    client_host = request.client.host if request.client else "unknown"
    # No aplicar rate limit a la ruta de health check
    if request.url.path != "/health":
        allowed = await rate_limit_middleware(client_host)
        if not allowed:
            return JSONResponse(status_code=429, content={"detail": "Rate limit exceeded"})
    logger.info(f"{request.method} {request.url} from {client_host}")
    try:
        response = await call_next(request)
    except Exception as e:
        logger.exception("Unhandled error in request")
        # Evitar sobreescribir excepciones HTTP que ya tienen una respuesta (como 401, 404, etc.)
        if isinstance(e, HTTPException):
            raise e
        return JSONResponse(status_code=500, content={"detail": "Internal Server Error"})
    elapsed = time.time() - start
    logger.info(f"{request.method} {request.url} completed_in={elapsed:.3f}s status={response.status_code}")
    return response

@app.get("/health", tags=["Infra"])
async def health():
    return {"status": "ok", "services": {
        "users": USERS_SVC, "posts": POSTS_SVC, "activities": ACTIVITIES_SVC, 
        "messages": MESSAGES_SVC, "events": EVENTS_SVC, "social": SOCIAL_SVC
    }}

# Centralized routing and proxying
@app.api_route("/{full_path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def catch_all(full_path: str, request: Request, token: Optional[str] = Depends(get_bearer_token)):
    # 1. Determinar el servicio de destino
    service_info = get_service_for_path(full_path)
    if not service_info:
        raise HTTPException(status_code=404, detail="Not found in gateway")

    # 2. Verificar si la ruta es pública
    is_public = service_info["path"] in service_info["public_paths"]
    
    # Las rutas de actividades son públicas para lectura (GET)
    if service_info["url"] == ACTIVITIES_SVC and request.method == "GET":
        is_public = True

    # 3. Validar autenticación para rutas no públicas
    if not is_public:
        if not token:
            raise HTTPException(status_code=401, detail="Not authenticated")
        payload = verify_jwt(token)
        # Aquí se podría añadir lógica de autorización basada en roles (ej. payload.get('roles'))

    # 4. Reenviar la petición al servicio correspondiente
    # El path que se pasa al servicio es el path completo original
    return await proxy_request(request, service_info["url"], full_path)

# Shutdown: close httpx client
@app.on_event("shutdown")
async def shutdown_event():
    await redis_client.close()
    await client.aclose()
