# 🗺️ Mapa de Servicios - Red Social Deportistas

## 📊 Diagrama de Arquitectura Completa

```
┌─────────────────────────────────────────────────────────────────────┐
│                         CAPA DE CLIENTE                             │
│                    (Navegador Web / Mobile App)                     │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             │ HTTP/HTTPS
                             │
        ┌────────────────────┴────────────────────┐
        │                                         │
        ▼                                         ▼
┌───────────────────┐                  ┌──────────────────────┐
│   DJANGO WEB      │                  │   API GATEWAY        │
│   Puerto 8000     │                  │   FastAPI :8080      │
│                   │                  │                      │
│ ┌───────────────┐ │                  │  Enrutador de        │
│ │   usuarios/   │ │                  │  Microservicios      │
│ │ publicaciones/│ │                  │                      │
│ │   eventos/    │ │                  └──────────┬───────────┘
│ │ seguimientos/ │ │                             │
│ └───────────────┘ │                             │
│                   │                             │
│  Django REST      │              ┌──────────────┼──────────────┐
│  Framework        │              │              │              │
└─────────┬─────────┘              ▼              ▼              ▼
          │                 ┌─────────────┐ ┌──────────┐ ┌──────────┐
          │                 │    Auth     │ │   Data   │ │  Notif.  │
          │                 │  Service    │ │   Mgmt   │ │  Service │
          │                 │   :8001     │ │  :8002   │ │  :8003   │
          │                 └─────────────┘ └────┬─────┘ └──────────┘
          │                                      │
          │                                      │
          ▼                                      ▼
┌─────────────────────┐              ┌──────────────────────┐
│   PostgreSQL DB     │              │  MongoDB / Redis     │
│     Puerto 5432     │              │  Bases alternativas  │
│                     │              │                      │
│  - usuarios         │              │  - Logs              │
│  - publicaciones    │              │  - Caché             │
│  - eventos          │              │  - Métricas          │
│  - seguimientos     │              │                      │
└─────────────────────┘              └──────────────────────┘
```

---

## 🎯 Flujos de Datos Principales

### 1. Flujo de Autenticación
```
Usuario ingresa credenciales
         │
         ▼
    Django Web (:8000)
         │
         ├─→ Valida contra Usuario model
         │
         ├─→ Crea sesión Django
         │
         └─→ [Futuro] API Gateway → Auth Service (JWT)
         │
         ▼
    Token/Sesión devuelto
```

### 2. Flujo de Publicación
```
Usuario crea post
         │
         ▼
    Django API (:8000/api/)
         │
         ├─→ Serializer valida datos
         │
         ├─→ Model guarda en PostgreSQL
         │
         ├─→ [Opcional] Notif Service → Avisa a seguidores
         │
         └─→ [Opcional] Analytics Service → Registra métrica
         │
         ▼
    Respuesta JSON al cliente
```

### 3. Flujo de Entrenamiento
```
Usuario inicia sesión
         │
         ▼
    SesionEntrenamiento (estado: activo)
         │
         ├─→ Usuario registra métricas en tiempo real
         │
         ├─→ Data Management Service → Caché Redis
         │
         └─→ Usuario finaliza sesión
         │
         ▼
    Publicacion auto-generada
         │
         ▼
    Analytics Service → Procesa estadísticas
```

### 4. Flujo de Evento
```
Usuario crea evento
         │
         ▼
    Django API (:8000/api/eventos/)
         │
         ├─→ EventoDeportivo guardado
         │
         └─→ Notif Service → Avisa a seguidores
         │
         ▼
    Otros usuarios se inscriben
         │
         ▼
    ParticipanteEvento creado
         │
         └─→ Notif Service → Confirma inscripción
```

---

## 🔌 Endpoints Principales

### Django REST API (Puerto 8000)

#### Usuarios
```
GET    /api/usuarios/                    # Listar usuarios
POST   /api/usuarios/                    # Crear usuario
GET    /api/usuarios/{id}/               # Detalle usuario
PUT    /api/usuarios/{id}/               # Actualizar usuario
DELETE /api/usuarios/{id}/               # Eliminar usuario
GET    /api/usuarios/{id}/perfil/        # Perfil deportista
```

#### Publicaciones
```
GET    /api/publicaciones/               # Feed de publicaciones
POST   /api/publicaciones/               # Crear publicación
GET    /api/publicaciones/{id}/          # Detalle publicación
POST   /api/publicaciones/{id}/like/     # Dar like
POST   /api/publicaciones/{id}/comentar/ # Comentar
GET    /api/entrenamientos/              # Sesiones de entrenamiento
POST   /api/entrenamientos/              # Iniciar entrenamiento
PUT    /api/entrenamientos/{id}/pausar/  # Pausar entrenamiento
PUT    /api/entrenamientos/{id}/finalizar/ # Finalizar entrenamiento
```

#### Eventos
```
GET    /api/eventos/                     # Listar eventos
POST   /api/eventos/                     # Crear evento
GET    /api/eventos/{id}/                # Detalle evento
POST   /api/eventos/{id}/inscribir/      # Inscribirse
DELETE /api/eventos/{id}/desinscribir/   # Desinscribirse
GET    /api/eventos/{id}/participantes/  # Listar participantes
```

#### Seguimientos
```
GET    /api/seguimientos/                # Mis seguimientos
POST   /api/seguimientos/                # Seguir usuario
DELETE /api/seguimientos/{id}/           # Dejar de seguir
GET    /api/usuarios/{id}/seguidores/    # Seguidores de usuario
GET    /api/usuarios/{id}/siguiendo/     # A quién sigue usuario
```

---

### API Gateway (Puerto 8080)

```
GET/POST  /api/v1/auth/{path}            # → Auth Service :8001
GET/POST  /api/v1/data/{path}            # → Data Management :8002
GET/POST  /api/v1/notifications/{path}   # → Notifications :8003
GET/POST  /api/v1/analytics/{path}       # → Analytics :8004
GET       /health                        # Health check del gateway
```

---

### Microservicios (FastAPI)

#### Authentication Service (:8001)
```
POST   /login                            # Login con JWT
POST   /register                         # Registro
POST   /refresh                          # Refresh token
GET    /verify                           # Verificar token
GET    /health                           # Health check
```

#### Data Management Service (:8002)
```
GET    /cache/{key}                      # Obtener de Redis
POST   /cache/{key}                      # Guardar en Redis
GET    /logs                             # Obtener logs (MongoDB)
POST   /logs                             # Guardar log (MongoDB)
GET    /health                           # Health check
```

#### Notifications Service (:8003)
```
POST   /send/email                       # Enviar email
POST   /send/push                        # Enviar push notification
POST   /send/realtime                    # Notificación en tiempo real
GET    /notifications/{user_id}          # Obtener notificaciones
GET    /health                           # Health check
```

#### Analytics Service (:8004)
```
GET    /stats/user/{id}                  # Estadísticas de usuario
GET    /stats/training/{id}              # Estadísticas de entrenamiento
GET    /stats/engagement                 # Métricas de engagement
POST   /track/event                      # Registrar evento
GET    /health                           # Health check
```

---

## 🗄️ Modelos de Datos

### Usuario y Perfil
```python
Usuario
├── id (PK)
├── username (unique)
├── email (unique)
├── password (hashed)
├── telefono
├── fecha_nacimiento
├── es_verificado
└── PerfilDeportista (1:1)
    ├── deporte_principal
    ├── nivel
    ├── biografia
    ├── foto_perfil
    └── redes_sociales
```

### Publicaciones
```python
Publicacion
├── id (PK)
├── autor (FK → Usuario)
├── contenido
├── imagen
├── tipo (normal/entrenamiento)
├── likes_count
├── comentarios_count
├── Like (1:N)
│   ├── usuario (FK)
│   └── fecha
├── Comentario (1:N)
│   ├── usuario (FK)
│   ├── contenido
│   └── fecha
└── SesionEntrenamiento (1:1)
    ├── deporte
    ├── estado
    ├── inicio/fin
    ├── distancia
    └── calorias
```

### Eventos
```python
EventoDeportivo
├── id (PK)
├── organizador (FK → Usuario)
├── titulo
├── descripcion
├── tipo
├── fecha_inicio/fin
├── ubicacion
├── capacidad_maxima
└── ParticipanteEvento (1:N)
    ├── usuario (FK)
    ├── confirmado
    └── fecha_registro
```

### Seguimientos
```python
Seguimiento
├── id (PK)
├── seguidor (FK → Usuario)
├── seguido (FK → Usuario)
└── fecha_creacion

Constraint: unique(seguidor, seguido)
Validación: seguidor ≠ seguido
```

---

## 🔐 Seguridad y Autenticación

### Actual (Django)
- **Sesiones**: Cookie-based sessions
- **CSRF**: Protección habilitada
- **Permisos**: IsAuthenticatedOrReadOnly
- **Passwords**: Hashing con PBKDF2

### Futuro (Microservicios)
- **JWT**: Tokens en Auth Service
- **OAuth2**: Integración con redes sociales
- **API Keys**: Para servicios externos
- **Rate Limiting**: Prevención de abuso

---

## 📦 Dependencias Principales

### Django
```
Django==4.2+
djangorestframework
django-cors-headers
django-filter
psycopg2-binary
python-decouple
Pillow
```

### FastAPI (Microservicios)
```
fastapi
uvicorn
pydantic
requests
```

### Data Management
```
pymongo          # MongoDB
redis            # Redis
sqlalchemy       # SQL ORM
```

---

## 🚀 Despliegue

### Desarrollo (Docker Compose)
```bash
docker-compose up -d
```

**Servicios levantados:**
- PostgreSQL: `localhost:5432`
- Django Web: `localhost:8000`
- (Futuro) API Gateway: `localhost:8080`
- (Futuro) Microservicios: `localhost:8001-8004`

### Producción (Sugerido)
```
┌─────────────┐
│   Nginx     │  → Reverse proxy
└──────┬──────┘
       │
       ├─→ Django (Gunicorn) × N instancias
       ├─→ API Gateway (Uvicorn)
       └─→ Microservicios (Uvicorn) × N instancias
       
PostgreSQL (Réplicas)
Redis (Cluster)
MongoDB (Replica Set)
```

---

## 📊 Monitoreo y Logs

### Health Checks
```
GET /health                    # Django
GET /api/v1/auth/health       # Auth Service
GET /api/v1/data/health       # Data Management
GET /api/v1/notifications/health  # Notifications
GET /api/v1/analytics/health  # Analytics
```

### Logs
- **Django**: Logs en consola/archivo
- **PostgreSQL**: Query logs
- **Microservicios**: Logs en MongoDB (Data Management)
- **Docker**: `docker-compose logs -f`

---

**Documento creado para visualizar la arquitectura de servicios**
