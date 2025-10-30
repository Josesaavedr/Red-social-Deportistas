from typing import Optional, Dict, Any
import os
import time
import asyncio
import logging

from fastapi import FastAPI, Request, HTTPException, Depends, Header, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
import httpx
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

# Rate limiting (simple, in-memory token bucket per IP)
RATE_LIMIT_CAPACITY = int(os.getenv("RATE_LIMIT_CAPACITY", "60"))  # requests
RATE_LIMIT_REFILL_SECONDS = int(os.getenv("RATE_LIMIT_REFILL_SECONDS", "60"))

# In-memory store: {key: (tokens, last_ts)}
_rate_store: Dict[str, Dict[str, Any]] = {}
_rate_lock = asyncio.Lock()

app = FastAPI(title="API Gateway - Red Social Deportistas", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Shared async HTTP client
client = httpx.AsyncClient(timeout=httpx.Timeout(10.0, connect=5.0))

# ---------------------- Utilidades ----------------------
async def check_rate_limit(key: str):
    async with _rate_lock:
        now = time.time()
        entry = _rate_store.get(key)
        if not entry:
            _rate_store[key] = {"tokens": RATE_LIMIT_CAPACITY - 1, "last": now}
            return True
        # refill
        elapsed = now - entry["last"]
        refill = (elapsed / RATE_LIMIT_REFILL_SECONDS) * RATE_LIMIT_CAPACITY
        if refill > 0:
            entry["tokens"] = min(RATE_LIMIT_CAPACITY, entry["tokens"] + refill)
            entry["last"] = now
        if entry["tokens"] >= 1:
            entry["tokens"] -= 1
            return True
        return False

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

async def proxy_request(request: Request, base_url: str, path: str, headers: dict):
    """Reenvía la petición al microservicio destino y devuelve la respuesta"""
    # Build URL
    url = base_url.rstrip("/") + "/" + path.lstrip("/")

    method = request.method
    body = request.stream()

    try:
        # Set a small retry policy for idempotent methods
        attempts = 2 if method in ("GET", "HEAD", "OPTIONS", "PUT", "DELETE") else 1
        for attempt in range(attempts):
            try:
                req = client.build_request(method, url, headers=headers, content=body, params=dict(request.query_params))
                resp = await client.send(req, stream=True)
                break
            except (httpx.ConnectError, httpx.ReadTimeout) as e:
                logger.warning(f"Attempt {attempt+1} failed for {url}: {e}")
                if attempt == attempts - 1:
                    raise
                await asyncio.sleep(0.2)
        # Stream response back
        return StreamingResponse(resp.aiter_bytes(), status_code=resp.status_code, headers=resp.headers)
    except httpx.HTTPError as e:
        logger.exception("Error proxying request")
        raise HTTPException(status_code=502, detail="Bad gateway")

# ---------------------- Endpoints ----------------------

@app.middleware("http")
async def add_logging_and_rate_limit(request: Request, call_next):
    start = time.time()
    client_host = request.client.host if request.client else "unknown"
    # No aplicar rate limit a la ruta de health check
    if request.url.path != "/health":
        key = client_host
        allowed = await check_rate_limit(key)
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
    # Define public routes that do not require a token
    public_routes = [
        ("POST", "users/login"),
        ("POST", "users/register"),
    ]

    is_public = any(
        request.method == method and full_path.startswith(path)
        for method, path in public_routes
    )

    # Route mapping
    service_map = {
        "users": USERS_SVC,
        "posts": POSTS_SVC,
        "activities": ACTIVITIES_SVC,
        "messages": MESSAGES_SVC,
        "events": EVENTS_SVC,
        "social": SOCIAL_SVC,
    }

    # Determine target service
    service_prefix = full_path.split('/')[0]
    base_url = service_map.get(service_prefix)

    if not base_url:
        raise HTTPException(status_code=404, detail="Not found in gateway")

    if not is_public:
        if not token:
            raise HTTPException(status_code=401, detail="Not authenticated")
        payload = verify_jwt(token)
        # TODO: Add more granular role-based access control here if needed

    # Copy headers - remove hop-by-hop headers
    headers = {k: v for k, v in request.headers.items() if k.lower() not in
               ("host", "connection", "keep-alive", "proxy-authenticate", "proxy-authorization", "te", "trailer", "transfer-encoding", "upgrade")}

    return await proxy_request(request, base_url, full_path, headers)

# Shutdown: close httpx client
@app.on_event("shutdown")
async def shutdown_event():
    await client.aclose()
