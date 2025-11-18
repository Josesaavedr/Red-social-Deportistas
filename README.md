## 👥 Autores

| Código | Nombre | Correo |
|:---|:---|:---|
|01| Jose Fernady Saavedra Duran|jose.saavedra.9076@miremington.edu.co|
|02| Narciso Yunda Yunda | narciso.yunda.7718@miremington.edu.co |

---
# Red Social Deportistas 🏃

Red social diseñada específicamente para deportistas, construida con Django, PostgreSQL y Docker.

## 🎯 Características

### Funcionalidades Principales
- **Gestión de Usuarios**: Sistema de registro y autenticación personalizado
- **Perfiles Deportivos**: Perfiles con información deportiva (deporte principal, nivel, biografía, etc.)
- **Publicaciones**: Sistema de publicaciones con imágenes, likes y comentarios
- **Sesiones de Entrenamiento**: Tracking de entrenamientos con métricas (distancia, calorías, tiempo)
- **Eventos Deportivos**: Creación y participación en eventos deportivos
- **Seguimientos**: Sistema para seguir a otros deportistas
- **API REST**: API completa con Django REST Framework

### Arquitectura de Microservicios
- **API Gateway**: Enrutador centralizado para microservicios
- **Authentication Service**: Autenticación JWT (en desarrollo)
- **Data Management Service**: Gestión multi-base de datos (SQL, MongoDB, Redis)
- **Notifications Service**: Sistema de notificaciones (plantilla)
- **Analytics Service**: Análisis y métricas deportivas (plantilla)

### Infraestructura
- **Docker**: Contenedorización completa con Docker y Docker Compose
- **PostgreSQL**: Base de datos principal
- **Arquitectura Híbrida**: Monolito modular + Microservicios

## 🛠️ Tecnologías

### Backend Principal
- **Django 4.2.7**: Framework web principal
- **Django REST Framework**: API RESTful
- **PostgreSQL 15**: Base de datos relacional
- **Python 3.11**: Lenguaje de programación

### Microservicios
- **FastAPI**: Framework para microservicios
- **MongoDB**: Base de datos NoSQL (data-management)
- **Redis**: Caché en memoria (data-management)

### DevOps
- **Docker**: Containerización
- **Docker Compose**: Orquestación de contenedores

## 📋 Requisitos Previos

- Docker
- Docker Compose

## 🚀 Instalación y Ejecución

### 1. Clonar el repositorio

```bash
git clone <url-del-repositorio>
cd Red-social-Deportistas
```

### 2. Configurar variables de entorno

Copia el archivo de ejemplo y configura las variables:

```bash
cp .env.example .env
```

Edita el archivo `.env` según tus necesidades (por defecto funciona con la configuración de docker-compose).

### 3. Construir y ejecutar con Docker Compose

```bash
docker-compose up --build
```

Esto construirá las imágenes y ejecutará todos los contenedores:
- **Base de datos PostgreSQL** en el puerto 5432
- **Aplicación Django** en el puerto 8000

### 4. Crear las migraciones y aplicar

En una nueva terminal:

```bash
docker-compose exec web python manage.py makemigrations
docker-compose exec web python manage.py migrate
```

### 5. Crear superusuario (opcional)

```bash
docker-compose exec web python manage.py createsuperuser
```

### 6. Acceder a la aplicación

- **Frontend**: http://localhost:8000
- **Admin Panel**: http://localhost:8000/admin
- **API**: http://localhost:8000/api/

## 📚 Documentación de Arquitectura

Este proyecto cuenta con documentación detallada de su arquitectura:

- **[📖 ARQUITECTURA_DETALLADA.md](ARQUITECTURA_DETALLADA.md)** - Explicación completa de la arquitectura, componentes y flujos de datos
- **[📂 GUIA_CARPETAS_Y_ARCHIVOS.md](GUIA_CARPETAS_Y_ARCHIVOS.md)** - Guía descriptiva de cada carpeta y archivo del proyecto
- **[🗺️ MAPA_SERVICIOS.md](MAPA_SERVICIOS.md)** - Diagramas visuales de servicios, endpoints y modelos de datos

## 📁 Estructura del Proyecto

```
Red-social-Deportistas/
├── deportistas_network/      # Configuración principal de Django
│   ├── settings.py           # Configuración del proyecto
│   ├── urls.py              # URLs principales
│   └── wsgi.py              # WSGI config
├── usuarios/                 # App de usuarios y perfiles
├── publicaciones/            # App de publicaciones
├── eventos/                  # App de eventos deportivos
├── seguimientos/             # App de seguimientos
├── services/                 # Microservicios FastAPI
│   ├── authentication/       # Servicio de autenticación JWT
│   ├── data-management/      # Gestión multi-DB (SQL, Mongo, Redis)
│   ├── notifications/        # Servicio de notificaciones
│   └── analytics/            # Servicio de análisis y métricas
├── api-gateway/             # Gateway de microservicios
├── frontend/                # Frontend Flask (opcional)
├── templates/               # Templates HTML Django
├── staticfiles/             # Archivos estáticos
├── media/                   # Archivos subidos por usuarios
├── manage.py               # Script de gestión de Django
├── requirements.txt        # Dependencias de Python
├── Dockerfile             # Configuración de Docker
└── docker-compose.yml     # Configuración de Docker Compose
```

> 💡 **Nota**: Los servicios `service1`, `service2` y `service3` han sido renombrados a `data-management`, `notifications` y `analytics` respectivamente para mayor claridad.

## 🔌 API Endpoints

### Usuarios
- `GET/POST /api/usuarios/` - Listar/Crear usuarios
- `GET/PUT/PATCH /api/usuarios/{id}/` - Detalle/Actualizar usuario
- `POST /api/usuarios/registro/` - Registro de nuevo usuario
- `GET /api/usuarios/perfil/` - Perfil del usuario autenticado

### Publicaciones
- `GET/POST /api/publicaciones/` - Listar/Crear publicaciones
- `GET/PUT/DELETE /api/publicaciones/{id}/` - Detalle/Actualizar/Eliminar publicación
- `POST /api/publicaciones/{id}/like/` - Dar/quitar like
- `POST /api/publicaciones/{id}/comentar/` - Agregar comentario

### Eventos
- `GET/POST /api/eventos/` - Listar/Crear eventos
- `GET/PUT/DELETE /api/eventos/{id}/` - Detalle/Actualizar/Eliminar evento
- `POST /api/eventos/{id}/participar/` - Participar en evento
- `DELETE /api/eventos/{id}/dejar_participar/` - Dejar de participar

### Seguimientos
- `GET /api/seguimientos/` - Listar seguimientos
- `POST /api/seguimientos/seguir/` - Seguir a un usuario
- `DELETE /api/seguimientos/dejar_seguir/` - Dejar de seguir
- `GET /api/seguimientos/seguidores/` - Listar seguidores
- `GET /api/seguimientos/siguiendo/` - Listar usuarios que sigues

## 🗄️ Modelos Principales

### Usuario
- Usuario personalizado extendiendo AbstractUser
- Campos: email, teléfono, fecha_nacimiento, es_verificado

### PerfilDeportista
- Perfil deportivo asociado a cada usuario
- Campos: deporte_principal, nivel, biografía, foto_perfil, ubicación, redes sociales

### Publicacion
- Publicaciones de los usuarios
- Campos: autor, contenido, imagen, fecha_creacion, likes_count, comentarios_count

### EventoDeportivo
- Eventos deportivos organizados
- Campos: organizador, título, descripción, tipo, fecha_inicio, fecha_fin, ubicación, capacidad_maxima

### Seguimiento
- Relación de seguimiento entre usuarios
- Campos: seguidor, seguido, fecha_creacion

## 🧪 Comandos Útiles

```bash
# Ver logs
docker-compose logs -f web

# Ejecutar comandos Django
docker-compose exec web python manage.py <comando>

# Acceder a la base de datos
docker-compose exec db psql -U deportistas_user -d deportistas_db

#levantar contenedores
docker-compose up -d

# Detener contenedores
docker-compose down

# Detener y eliminar volúmenes
docker-compose down -v
```

## 📝 Licencia

Este proyecto es parte de un seminario académico.

## 🔒 Seguridad

- ⚠️ **Importante**: Cambiar `SECRET_KEY` en producción
- ⚠️ Configurar `DEBUG=False` en producción
- ⚠️ Configurar `ALLOWED_HOSTS` apropiadamente
- ⚠️ Usar variables de entorno para datos sensibles

## 🐛 Solución de Problemas

### Error de conexión a la base de datos
Asegúrate de que el contenedor de PostgreSQL esté corriendo:
```bash
docker-compose ps
```

### Error de migraciones
Ejecuta las migraciones manualmente:
```bash
docker-compose exec web python manage.py makemigrations
docker-compose exec web python manage.py migrate
```

### Limpiar y reconstruir
```bash
docker-compose down -v
docker-compose up --build
```
