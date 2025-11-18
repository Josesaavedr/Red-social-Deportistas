# 📂 Guía Rápida de Carpetas y Archivos

## 🎯 Resumen Ejecutivo

Este proyecto es una **Red Social para Deportistas** con arquitectura híbrida:
- **Django** (aplicación principal monolítica modular)
- **FastAPI** (microservicios independientes)
- **PostgreSQL** (base de datos)
- **Docker** (containerización)

---

## 📁 Estructura Visual

```
Red-social-Deportistas/
│
├── 🐍 APLICACIÓN DJANGO (Backend Principal)
│   ├── deportistas_network/        → Configuración del proyecto
│   ├── usuarios/                   → Gestión de usuarios y perfiles
│   ├── publicaciones/              → Posts, likes, comentarios, entrenamientos
│   ├── eventos/                    → Eventos deportivos
│   └── seguimientos/               → Sistema de seguir/seguidores
│
├── ⚡ MICROSERVICIOS (FastAPI)
│   ├── services/authentication/    → Autenticación JWT
│   ├── services/data-management/   → Multi-DB (SQL, Mongo, Redis)
│   ├── services/notifications/     → Notificaciones (plantilla)
│   └── services/analytics/         → Análisis y métricas (plantilla)
│
├── 🌐 API GATEWAY
│   └── api-gateway/                → Enrutador de microservicios
│
├── 🎨 FRONTEND
│   ├── frontend/                   → App Flask (opcional)
│   ├── templates/                  → Templates HTML Django
│   ├── staticfiles/                → CSS, JS, imágenes
│   └── media/                      → Archivos subidos por usuarios
│
└── 🔧 CONFIGURACIÓN
    ├── docker-compose.yml          → Orquestación de servicios
    ├── Dockerfile                  → Imagen Docker Django
    ├── requirements.txt            → Dependencias Python
    └── manage.py                   → CLI de Django
```

---

## 🗂️ Descripción de Carpetas Principales

### 1️⃣ **deportistas_network/** - Configuración Django
**¿Qué hace?** Configuración central del proyecto Django

| Archivo | Propósito |
|---------|-----------|
| `settings.py` | Configuración global: DB, apps, middleware, autenticación |
| `urls.py` | Enrutamiento principal de URLs |
| `wsgi.py` / `asgi.py` | Interfaces para servidores web |

**Configuraciones importantes:**
- Base de datos PostgreSQL
- Modelo de usuario personalizado
- Django REST Framework
- CORS habilitado
- Zona horaria: America/Bogota

---

### 2️⃣ **usuarios/** - Gestión de Usuarios
**¿Qué hace?** Maneja usuarios, autenticación y perfiles deportivos

**Modelos:**
- `Usuario`: Autenticación, email, teléfono, verificación
- `PerfilDeportista`: Deporte, nivel, biografía, fotos, redes sociales

**Archivos clave:**
- `models.py`: Define estructura de datos
- `views.py`: API REST endpoints
- `views_web.py`: Vistas HTML
- `serializers.py`: Conversión JSON ↔ Python
- `forms.py`: Formularios web

**Funcionalidad:**
✅ Registro y login  
✅ Perfiles deportivos personalizados  
✅ Fotos de perfil y portada  
✅ Integración con redes sociales  

---

### 3️⃣ **publicaciones/** - Contenido Social
**¿Qué hace?** Sistema de publicaciones, likes, comentarios y entrenamientos

**Modelos:**
- `Publicacion`: Posts con texto e imagen
- `Like`: Sistema de "me gusta"
- `Comentario`: Comentarios en publicaciones
- `SesionEntrenamiento`: Tracking de entrenamientos con métricas

**Funcionalidad:**
✅ Feed de publicaciones  
✅ Likes y comentarios  
✅ Registro de entrenamientos (distancia, calorías, tiempo)  
✅ Generación automática de posts desde entrenamientos  

---

### 4️⃣ **eventos/** - Eventos Deportivos
**¿Qué hace?** Organización y participación en eventos

**Modelos:**
- `EventoDeportivo`: Competiciones, torneos, entrenamientos grupales
- `ParticipanteEvento`: Inscripciones a eventos

**Funcionalidad:**
✅ Crear eventos con fecha, ubicación, capacidad  
✅ Inscripción de participantes  
✅ Control de aforo  
✅ Eventos públicos/privados  

---

### 5️⃣ **seguimientos/** - Red Social
**¿Qué hace?** Sistema de seguir a otros usuarios

**Modelo:**
- `Seguimiento`: Relación seguidor ↔ seguido

**Funcionalidad:**
✅ Seguir/dejar de seguir usuarios  
✅ Listar seguidores y seguidos  
✅ Validación (no auto-seguimiento)  

---

### 6️⃣ **services/authentication/** - Autenticación
**¿Qué hace?** Microservicio de autenticación con FastAPI

**Tecnología:** FastAPI  
**Puerto:** 8001  

**Estado:** En desarrollo (plantilla básica)

**Propósito futuro:**
- Autenticación JWT
- Refresh tokens
- OAuth2
- Separación de responsabilidades

---

### 7️⃣ **services/data-management/** - Gestión de Datos
**¿Qué hace?** Microservicio para múltiples bases de datos

**Tecnología:** FastAPI  
**Puerto:** 8002  

**Archivos:**
- `database_sql.py`: Conexión PostgreSQL/MySQL
- `database_mongo.py`: Conexión MongoDB
- `database_redis.py`: Conexión Redis (caché)

**Casos de uso:**
- Caché de datos frecuentes (Redis)
- Logs y métricas no estructuradas (MongoDB)
- Datos relacionales complementarios (SQL)
- Estadísticas de rendimiento

---

### 8️⃣ **services/notifications/** - Notificaciones
**¿Qué hace?** Microservicio de notificaciones (plantilla)

**Tecnología:** FastAPI  
**Puerto:** 8003  

**Estado:** Plantilla para implementar

**Propósito futuro:**
- Notificaciones push
- Emails automáticos
- Notificaciones en tiempo real (WebSockets)
- Alertas de eventos, seguidores, likes

---

### 9️⃣ **services/analytics/** - Análisis
**¿Qué hace?** Microservicio de análisis y métricas (plantilla)

**Tecnología:** FastAPI  
**Puerto:** 8004  

**Estado:** Plantilla para implementar

**Propósito futuro:**
- Estadísticas de rendimiento deportivo
- Análisis de progreso
- Métricas de engagement
- Dashboards y reportes

---

### 🔟 **api-gateway/** - Gateway de Microservicios
**¿Qué hace?** Punto de entrada único para todos los microservicios

**Tecnología:** FastAPI  
**Puerto:** 8080  

**Funcionalidad:**
- Enrutamiento: `/api/v1/{service_name}/{path}`
- Forwarding de peticiones GET/POST
- CORS centralizado
- Health checks

**Ejemplo de uso:**
```
GET /api/v1/auth/login → http://auth-service:8001/login
POST /api/v1/notifications/send → http://notifications-service:8003/send
```

---

## 🔄 Flujo de Trabajo Típico

### Crear una Publicación
```
Usuario → Django (puerto 8000)
       → views.py valida datos
       → models.py guarda en PostgreSQL
       → Respuesta al usuario
       → [Opcional] Notificación a seguidores (microservicio)
```

### Registrar Entrenamiento
```
Usuario inicia sesión → SesionEntrenamiento (estado: activo)
                     → Usuario registra métricas
                     → Usuario finaliza
                     → Se crea Publicacion automáticamente
                     → [Opcional] Analytics procesa datos
```

---

## 🐳 Docker y Despliegue

### docker-compose.yml
Define 2 servicios principales:
1. **db**: PostgreSQL 15
2. **web**: Aplicación Django

**Volúmenes:**
- `postgres_data`: Persistencia de base de datos
- `static_volume`: Archivos estáticos
- `media_volume`: Archivos de usuarios

### Dockerfile
Construye imagen de Django:
- Python 3.11+
- Instala dependencias
- Copia código
- Expone puerto 8000

### entrypoint.sh
Script de inicio:
1. Espera a que PostgreSQL esté listo
2. Ejecuta migraciones
3. Recolecta archivos estáticos
4. Inicia servidor Django

---

## 📊 Base de Datos (PostgreSQL)

**Configuración:**
- Host: `db` (en Docker) / `localhost` (local)
- Puerto: 5432
- Base de datos: `deportistas_db`
- Usuario: `deportistas_user`

**Tablas principales:**
- `usuarios_usuario`
- `usuarios_perfildeportista`
- `publicaciones_publicacion`
- `publicaciones_like`
- `publicaciones_comentario`
- `publicaciones_sesionentrenamiento`
- `eventos_eventodeportivo`
- `eventos_participanteevento`
- `seguimientos_seguimiento`

---

## 🛠️ Archivos de Configuración

| Archivo | Propósito |
|---------|-----------|
| `requirements.txt` | Dependencias Python producción |
| `requirements-dev.txt` | Dependencias desarrollo |
| `manage.py` | CLI Django (migraciones, servidor, shell) |
| `.env` | Variables de entorno (no incluido en repo) |

---

## 🚀 Comandos Útiles

```bash
# Iniciar con Docker
docker-compose up -d

# Migraciones
python manage.py makemigrations
python manage.py migrate

# Crear superusuario
python manage.py createsuperuser

# Servidor de desarrollo
python manage.py runserver

# Shell interactivo
python manage.py shell

# Recolectar archivos estáticos
python manage.py collectstatic
```

---

## 📈 Escalabilidad

**Actual:**
- Monolito Django modular
- PostgreSQL single instance
- Microservicios preparados (plantillas)

**Futuro:**
- Múltiples instancias Django (load balancer)
- PostgreSQL con réplicas
- Redis para caché distribuido
- Microservicios completamente implementados
- Message queue (RabbitMQ/Kafka)

---

**Documento creado para facilitar la comprensión del proyecto**
