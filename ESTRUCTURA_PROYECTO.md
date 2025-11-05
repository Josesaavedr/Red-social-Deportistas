# 📁 Estructura del Proyecto - Red Social Deportistas

## Estructura Principal

```
Red-social-Deportistas/
│
├── deportistas_network/          # Configuración principal de Django
│   ├── __init__.py
│   ├── settings.py              # Configuración del proyecto
│   ├── urls.py                  # URLs principales
│   ├── wsgi.py                  # WSGI config
│   ├── asgi.py                  # ASGI config
│   └── admin.py                 # Configuración del admin
│
├── usuarios/                     # App de usuarios y perfiles
│   ├── models.py                # Usuario, PerfilDeportista
│   ├── views.py                 # ViewSets para API
│   ├── views_web.py             # Vistas web (login, registro)
│   ├── serializers.py          # Serializers para API
│   ├── forms.py                 # Formularios web
│   ├── urls.py                  # URLs API
│   ├── urls_web.py              # URLs web
│   └── admin.py                 # Configuración admin
│
├── publicaciones/               # App de publicaciones
│   ├── models.py                # Publicacion, Like, Comentario
│   ├── views.py                 # ViewSets para API
│   ├── serializers.py          # Serializers
│   ├── urls.py                  # URLs API
│   ├── urls_web.py              # URLs web
│   └── admin.py                 # Configuración admin
│
├── eventos/                      # App de eventos deportivos
│   ├── models.py                # EventoDeportivo, ParticipanteEvento
│   ├── views.py                 # ViewSets para API
│   ├── serializers.py          # Serializers
│   ├── urls.py                  # URLs API
│   └── admin.py                 # Configuración admin
│
├── seguimientos/                 # App de seguimientos
│   ├── models.py                # Seguimiento
│   ├── views.py                 # ViewSets para API
│   ├── serializers.py          # Serializers
│   ├── urls.py                  # URLs API
│   └── admin.py                 # Configuración admin
│
├── templates/                    # Templates HTML
│   ├── base.html                # Template base
│   ├── publicaciones/
│   │   └── feed.html            # Página principal
│   └── usuarios/
│       ├── login.html           # Página de login
│       └── registro.html        # Página de registro
│
├── manage.py                     # Script de gestión de Django
├── requirements.txt              # Dependencias Python
├── Dockerfile                    # Configuración Docker
├── docker-compose.yml            # Configuración Docker Compose
├── entrypoint.sh                 # Script de inicio
├── .env.example                  # Ejemplo de variables de entorno
├── README.md                     # Documentación principal
├── INICIO_RAPIDO.md             # Guía de inicio rápido
└── ESTRUCTURA_PROYECTO.md       # Este archivo
```

## Apps de Django

### 1. usuarios
- **Modelos**: `Usuario`, `PerfilDeportista`
- **Funcionalidades**: Registro, autenticación, gestión de perfiles deportivos

### 2. publicaciones
- **Modelos**: `Publicacion`, `Like`, `Comentario`
- **Funcionalidades**: Crear publicaciones, likes, comentarios

### 3. eventos
- **Modelos**: `EventoDeportivo`, `ParticipanteEvento`
- **Funcionalidades**: Crear eventos, participar en eventos

### 4. seguimientos
- **Modelos**: `Seguimiento`
- **Funcionalidades**: Seguir/dejar de seguir usuarios

## Base de Datos

- **Motor**: PostgreSQL 15
- **Ubicación**: Contenedor Docker `deportistas_db`
- **Puerto**: 5432

## Archivos de Configuración

- **docker-compose.yml**: Orquestación de servicios
- **Dockerfile**: Imagen Docker de la aplicación
- **entrypoint.sh**: Script de inicio automático
- **settings.py**: Configuración completa de Django

## Endpoints API

Ver `README.md` para documentación completa de endpoints.

## Notas

- Los archivos en `api-gateway/`, `services/`, `frontend/`, y `common/` son de la plantilla original y pueden ser eliminados si no se necesitan.
- El proyecto está completamente funcional con Docker Compose.

