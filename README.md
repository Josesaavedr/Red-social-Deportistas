## 👥 Autores

| Código | Nombre | Correo |
|:---|:---|:---|
|01| Jose Fernady Saavedra Duran|jose.saavedra.9076@miremington.edu.co|
|02| Narciso Yunda Yunda | narciso.yunda.7718@miremington.edu.co |

---
# Red Social Deportistas 🏃

Red social diseñada específicamente para deportistas, construida con Django, PostgreSQL y Docker.

## 🎯 Características

- **Gestión de Usuarios**: Sistema de registro y autenticación personalizado
- **Perfiles Deportivos**: Perfiles con información deportiva (deporte principal, nivel, biografía, etc.)
- **Publicaciones**: Sistema de publicaciones con imágenes, likes y comentarios
- **Eventos Deportivos**: Creación y participación en eventos deportivos
- **Seguimientos**: Sistema para seguir a otros deportistas
- **API REST**: API completa con Django REST Framework
- **Docker**: Contenedorización completa con Docker y Docker Compose

## 🛠️ Tecnologías

- **Backend**: Django 4.2.7
- **Base de Datos**: PostgreSQL 15
- **API**: Django REST Framework
- **Contenedores**: Docker & Docker Compose
- **Python**: 3.11

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

## 📚 Estructura del Proyecto

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
├── templates/                # Templates HTML
├── manage.py                # Script de gestión de Django
├── requirements.txt         # Dependencias de Python
├── Dockerfile              # Configuración de Docker
└── docker-compose.yml      # Configuración de Docker Compose
```

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
