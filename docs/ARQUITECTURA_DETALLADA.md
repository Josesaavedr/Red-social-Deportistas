# 🏗️ Arquitectura Detallada - Red Social para Deportistas

## 📋 Índice
1. [Visión General](#visión-general)
2. [Arquitectura del Sistema](#arquitectura-del-sistema)
3. [Estructura de Carpetas y Componentes](#estructura-de-carpetas)
4. [Flujo de Datos](#flujo-de-datos)
5. [Tecnologías Utilizadas](#tecnologías-utilizadas)

---

## Visión General

Este proyecto es una **Red Social para Deportistas** construida con una arquitectura híbrida que combina:
- **Django** como framework principal (monolito modular)
- **Microservicios FastAPI** para funcionalidades específicas
- **API Gateway** para enrutamiento de microservicios
- **PostgreSQL** como base de datos principal
- **Docker** para containerización

### Propósito del Sistema
Plataforma social donde deportistas pueden:
- Crear perfiles deportivos personalizados
- Publicar contenido y sesiones de entrenamiento
- Seguir a otros deportistas
- Organizar y participar en eventos deportivos
- Interactuar mediante likes y comentarios

---

## Arquitectura del Sistema

```
┌─────────────────────────────────────────────────────────────┐
│                        CLIENTE WEB                          │
│                    (Navegador/Frontend)                     │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                   APLICACIÓN DJANGO                         │
│              (Puerto 8000 - Monolito)                       │
│  ┌──────────┬──────────┬──────────┬──────────────────┐    │
│  │ Usuarios │ Publicac.│ Eventos  │ Seguimientos     │    │
│  └──────────┴──────────┴──────────┴──────────────────┘    │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                  BASE DE DATOS PostgreSQL                   │
│                      (Puerto 5432)                          │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                    API GATEWAY (FastAPI)                    │
│                      (Puerto 8080)                          │
└────────────┬────────────┬────────────┬─────────────────────┘
             │            │            │
             ▼            ▼            ▼
    ┌────────────┐ ┌────────────┐ ┌────────────┐
    │   Auth     │ │Data Mgmt   │ │Notificac.  │
    │  Service   │ │  Service   │ │  Service   │
    └────────────┘ └────────────┘ └────────────┘
```

---

## 📁 Estructura de Carpetas

### **Raíz del Proyecto**
```
Red-social-Deportistas/
├── 📄 manage.py                    # Script principal de Django
├── 📄 docker-compose.yml           # Orquestación de contenedores
├── 📄 Dockerfile                   # Imagen Docker para Django
├── 📄 requirements.txt             # Dependencias Python principales
├── 📄 requirements-dev.txt         # Dependencias de desarrollo
└── 📄 entrypoint.sh               # Script de inicio del contenedor
```

**Utilidad:**
- `manage.py`: Punto de entrada para comandos Django (migraciones, servidor, etc.)
- `docker-compose.yml`: Define y conecta todos los servicios (web, db, microservicios)
- `Dockerfile`: Instrucciones para construir la imagen Docker de Django
- `requirements.txt`: Lista de paquetes Python necesarios para producción
- `entrypoint.sh`: Ejecuta migraciones y arranca el servidor al iniciar el contenedor

---

### **deportistas_network/** 
**Configuración principal de Django**

```
deportistas_network/
├── __init__.py                     # Marca el directorio como paquete Python
├── settings.py                     # Configuración global del proyecto
├── urls.py                         # Enrutamiento principal de URLs
├── wsgi.py                         # Interfaz WSGI para servidores de producción
└── asgi.py                         # Interfaz ASGI para aplicaciones asíncronas
```

**Utilidad:**
- `settings.py`: Configura base de datos, apps instaladas, middleware, autenticación, CORS, archivos estáticos
- `urls.py`: Define las rutas principales y distribuye a las apps
- `wsgi.py/asgi.py`: Interfaces para servidores web (Gunicorn, Uvicorn, etc.)

**Configuraciones clave en settings.py:**
- Modelo de usuario personalizado: `AUTH_USER_MODEL = 'usuarios.Usuario'`
- Base de datos PostgreSQL configurada con variables de entorno
- Django REST Framework con autenticación por sesión
- CORS habilitado para desarrollo
- Zona horaria: America/Bogota

---

### **usuarios/** 
**Gestión de usuarios y perfiles deportivos**

```
usuarios/
├── models.py                       # Modelos: Usuario, PerfilDeportista
├── views.py                        # Vistas API REST
├── views_web.py                    # Vistas web (templates)
├── serializers.py                  # Serializadores DRF
├── urls.py                         # URLs API
├── urls_web.py                     # URLs web
├── forms.py                        # Formularios Django
├── admin.py                        # Configuración del admin
└── migrations/                     # Migraciones de base de datos
```

**Modelos:**
1. **Usuario** (extiende AbstractUser de Django)
   - Campos: email único, teléfono, fecha_nacimiento, es_verificado
   - Autenticación y autorización base del sistema

2. **PerfilDeportista** (relación 1:1 con Usuario)
   - Deporte principal y secundarios
   - Nivel deportivo (principiante → profesional)
   - Biografía, fotos (perfil y portada)
   - Redes sociales (Instagram, Twitter)
   - Ubicación y sitio web

**Funcionalidad:**
- Registro y autenticación de usuarios
- Gestión de perfiles deportivos
- API REST para operaciones CRUD
- Vistas web con templates HTML

---

### **publicaciones/**
**Sistema de publicaciones y entrenamientos**

```
publicaciones/
├── models.py                       # Modelos: Publicacion, Like, Comentario, SesionEntrenamiento
├── views.py                        # API REST endpoints
├── views_web.py                    # Vistas web
├── serializers.py                  # Serializadores DRF
├── urls.py                         # URLs API
├── urls_web.py                     # URLs web
├── admin.py                        # Panel de administración
└── migrations/                     # Migraciones
```

**Modelos:**
1. **Publicacion**
   - Contenido de texto (max 2000 caracteres)
   - Imagen opcional
   - Tipo: normal o entrenamiento
   - Contadores: likes_count, comentarios_count
   - Timestamps automáticos

2. **Like**
   - Relación usuario-publicación
   - Constraint único (un like por usuario por publicación)

3. **Comentario**
   - Contenido (max 1000 caracteres)
   - Relación con usuario y publicación
   - Ordenados cronológicamente

4. **SesionEntrenamiento**
   - Deporte y estado (activo, pausado, completado, cancelado)
   - Tiempos: inicio, fin, tiempo_pausado
   - Métricas: distancia (km), calorías
   - Vinculada a una Publicacion

**Funcionalidad:**
- Feed de publicaciones
- Sistema de likes y comentarios
- Tracking de sesiones de entrenamiento en tiempo real
- Generación automática de publicaciones desde entrenamientos

---

### **eventos/**
**Organización de eventos deportivos**

```
eventos/
├── models.py                       # Modelos: EventoDeportivo, ParticipanteEvento
├── views.py                        # API REST
├── views_web.py                    # Vistas web
├── serializers.py                  # Serializadores
├── urls.py                         # URLs API
├── urls_web.py                     # URLs web
├── admin.py                        # Admin
└── migrations/                     # Migraciones
```

**Modelos:**
1. **EventoDeportivo**
   - Título, descripción, tipo (competición, entrenamiento, torneo, etc.)
   - Fechas: inicio y fin
   - Ubicación física
   - Capacidad máxima y contador de participantes
   - Visibilidad: público/privado
   - Organizador (ForeignKey a Usuario)

2. **ParticipanteEvento**
   - Relación usuario-evento
   - Estado de confirmación
   - Fecha de registro

**Funcionalidad:**
- Creación y gestión de eventos deportivos
- Sistema de inscripción de participantes
- Control de capacidad
- Filtrado por fecha, tipo, ubicación

---

### **seguimientos/**
**Sistema de seguimiento entre usuarios**

```
seguimientos/
├── models.py                       # Modelo: Seguimiento
├── views.py                        # API REST
├── serializers.py                  # Serializadores
├── urls.py                         # URLs
├── admin.py                        # Admin
└── migrations/                     # Migraciones
```

**Modelo:**
- **Seguimiento**
  - Seguidor (quien sigue)
  - Seguido (a quien siguen)
  - Constraint único (no duplicar seguimientos)
  - Validación: usuario no puede seguirse a sí mismo

**Funcionalidad:**
- Seguir/dejar de seguir usuarios
- Listar seguidores y seguidos
- Base para feed personalizado

---

### **services/**
**Microservicios FastAPI**

#### **services/authentication/**
**Servicio de autenticación (FastAPI)**

```
authentication/
├── main.py                         # Aplicación FastAPI
├── Dockerfile                      # Imagen Docker
└── requirements.txt                # Dependencias
```

**Utilidad:**
- Microservicio para autenticación JWT (en desarrollo)
- Endpoint de health check
- Separación de responsabilidades de autenticación

---

#### **services/data-management/** (antes service1)
**Servicio de gestión de datos multi-base de datos**

```
data-management/
├── main.py                         # Aplicación FastAPI
├── models.py                       # Modelos Pydantic
├── database_sql.py                 # Conexión SQL (PostgreSQL/MySQL)
├── database_mongo.py               # Conexión MongoDB
├── database_redis.py               # Conexión Redis (caché)
├── Dockerfile                      # Imagen Docker
└── requirements.txt                # Dependencias
```

**Utilidad:**
- Gestión de múltiples tipos de bases de datos
- Caché con Redis para datos frecuentes
- MongoDB para datos no estructurados (logs, métricas)
- SQL para datos relacionales complementarios
- Ideal para: estadísticas, caché de sesiones, logs de actividad

---

#### **services/notifications/** (antes service2)
**Servicio de notificaciones (plantilla)**

```
notifications/
├── main.py                         # Aplicación FastAPI
├── models.py                       # Modelos Pydantic
├── Dockerfile                      # Imagen Docker
└── requirements.txt                # Dependencias
```

**Utilidad (propuesta):**
- Envío de notificaciones push
- Notificaciones por email
- Notificaciones en tiempo real (WebSockets)
- Alertas de eventos, nuevos seguidores, likes, comentarios

---

#### **services/analytics/** (antes service3)
**Servicio de análisis y métricas (plantilla)**

```
analytics/
├── main.py                         # Aplicación FastAPI
├── models.py                       # Modelos Pydantic
├── Dockerfile                      # Imagen Docker
└── requirements.txt                # Dependencias
```

**Utilidad (propuesta):**
- Análisis de rendimiento deportivo
- Estadísticas de usuario (entrenamientos, progreso)
- Métricas de engagement (likes, comentarios, seguidores)
- Reportes y dashboards

---

### **api-gateway/**
**Gateway de microservicios**

```
api-gateway/
├── main.py                         # Aplicación FastAPI
├── Dockerfile                      # Imagen Docker
└── requirements.txt                # Dependencias
```

**Utilidad:**
- Punto de entrada único para todos los microservicios
- Enrutamiento dinámico: `/api/v1/{service_name}/{path}`
- Manejo de CORS
- Forwarding de peticiones GET y POST
- Health check centralizado

**Configuración:**
```python
SERVICES = {
    "auth": "http://auth-service:8001",
    "data": "http://data-service:8002",
    "notifications": "http://notifications-service:8003",
    "analytics": "http://analytics-service:8004",
}
```

---

### **frontend/**
**Aplicación frontend (Flask - opcional)**

```
frontend/
├── app.py                          # Aplicación Flask
├── Dockerfile                      # Imagen Docker
├── requirements.txt                # Dependencias
├── templates/                      # Templates HTML
└── static/                         # CSS, JS, imágenes
```

**Utilidad:**
- Frontend alternativo con Flask
- Consume APIs de Django y microservicios
- Separación frontend/backend

---

### **templates/**
**Templates HTML de Django**

```
templates/
├── base.html                       # Template base (herencia)
├── usuarios/                       # Templates de usuarios
├── publicaciones/                  # Templates de publicaciones
└── eventos/                        # Templates de eventos
```

**Utilidad:**
- Vistas web renderizadas por Django
- Sistema de herencia de templates
- Interfaz web tradicional (server-side rendering)

---

### **staticfiles/** y **media/**

```
staticfiles/                        # Archivos estáticos (CSS, JS)
media/                              # Archivos subidos por usuarios
├── perfiles/                       # Fotos de perfil
├── portadas/                       # Fotos de portada
├── publicaciones/                  # Imágenes de publicaciones
└── eventos/                        # Imágenes de eventos
```

**Utilidad:**
- `staticfiles/`: Archivos estáticos recolectados con `collectstatic`
- `media/`: Contenido generado por usuarios (imágenes, archivos)

---

### **common/**
**Código compartido**

```
common/
├── config.py                       # Configuraciones compartidas
└── helpers/                        # Funciones auxiliares
```

**Utilidad:**
- Código reutilizable entre apps
- Configuraciones comunes
- Utilidades y helpers

---

## 🔄 Flujo de Datos

### Flujo de una Publicación

```
1. Usuario crea publicación (Web/API)
   ↓
2. Django recibe request → views.py
   ↓
3. Validación con serializers.py
   ↓
4. Guardado en PostgreSQL (models.py)
   ↓
5. Respuesta JSON/HTML al cliente
   ↓
6. [Opcional] Notificación a seguidores (microservicio)
   ↓
7. [Opcional] Actualización de analytics (microservicio)
```

### Flujo de Autenticación

```
1. Usuario envía credenciales
   ↓
2. Django valida contra modelo Usuario
   ↓
3. Genera token/sesión
   ↓
4. [Futuro] API Gateway → Auth Service (JWT)
   ↓
5. Token devuelto al cliente
   ↓
6. Cliente incluye token en requests subsecuentes
```

---

## 🛠️ Tecnologías Utilizadas

### Backend
- **Django 4.2+**: Framework web principal
- **Django REST Framework**: APIs RESTful
- **FastAPI**: Microservicios de alto rendimiento
- **PostgreSQL 15**: Base de datos relacional
- **Redis**: Caché (en data-management)
- **MongoDB**: Base de datos NoSQL (en data-management)

### Frontend
- **HTML/CSS/JavaScript**: Templates Django
- **Flask**: Frontend alternativo (opcional)

### DevOps
- **Docker**: Containerización
- **Docker Compose**: Orquestación multi-contenedor
- **Gunicorn/Uvicorn**: Servidores WSGI/ASGI

### Librerías Python
- `python-decouple`: Variables de entorno
- `Pillow`: Procesamiento de imágenes
- `django-cors-headers`: CORS
- `django-filter`: Filtrado avanzado
- `requests`: HTTP client para API Gateway

---

## 🚀 Cómo Funciona el Sistema

### Inicio del Sistema
1. **Docker Compose** levanta todos los servicios
2. **PostgreSQL** inicia primero (healthcheck)
3. **Django** espera a que DB esté lista
4. **Migraciones** se ejecutan automáticamente (entrypoint.sh)
5. **Servidor Django** arranca en puerto 8000
6. **Microservicios** arrancan en sus puertos respectivos
7. **API Gateway** se conecta a los microservicios

### Operación Normal
- **Requests web** → Django (puerto 8000)
- **Requests API REST** → Django DRF (puerto 8000/api/)
- **Requests microservicios** → API Gateway (puerto 8080) → Microservicio específico

### Escalabilidad
- Django puede escalar horizontalmente (múltiples instancias)
- Microservicios independientes y escalables
- PostgreSQL puede configurarse con réplicas
- Redis para caché distribuido

---

## 📊 Diagrama de Base de Datos

```
Usuario (1) ←→ (1) PerfilDeportista
   ↓ (1:N)
Publicacion
   ↓ (1:N)
Like, Comentario

Usuario (1) ←→ (N) EventoDeportivo (organizador)
   ↓ (N:M)
ParticipanteEvento

Usuario (N) ←→ (M) Usuario (Seguimiento)
   seguidor ←→ seguido
```

---

## 🎯 Casos de Uso Principales

1. **Registro y Perfil**
   - Usuario se registra → crea perfil deportivo → sube fotos

2. **Publicaciones**
   - Usuario crea publicación → otros ven en feed → dan like/comentan

3. **Entrenamientos**
   - Usuario inicia sesión → registra métricas → finaliza → genera publicación

4. **Eventos**
   - Usuario crea evento → otros se inscriben → organizador gestiona participantes

5. **Red Social**
   - Usuario sigue a otros → ve publicaciones de seguidos → interactúa

---

## 🔐 Seguridad

- Autenticación por sesión (Django)
- CSRF protection habilitado
- Validación de datos con serializers
- Permisos por usuario (IsAuthenticatedOrReadOnly)
- Variables de entorno para secretos
- CORS configurado

---

## 📝 Próximos Pasos Sugeridos

1. **Implementar microservicios**:
   - Completar authentication service con JWT
   - Desarrollar notifications service
   - Implementar analytics service

2. **Mejorar frontend**:
   - SPA con React/Vue
   - WebSockets para notificaciones en tiempo real

3. **Optimizaciones**:
   - Implementar caché con Redis
   - Optimizar queries con select_related/prefetch_related
   - Añadir índices de base de datos

4. **Testing**:
   - Tests unitarios para cada app
   - Tests de integración
   - Tests E2E

---

**Documento creado para explicar la arquitectura completa del proyecto Red Social para Deportistas**
