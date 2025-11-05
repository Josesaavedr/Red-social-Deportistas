# 🚀 Inicio Rápido - Red Social Deportistas

## Pasos para ejecutar el proyecto

### 1. Clonar y configurar

```bash
# Clonar el repositorio
git clone <url-del-repositorio>
cd Red-social-Deportistas

# Copiar archivo de variables de entorno
cp .env.example .env
```

### 2. Levantar con Docker Compose

```bash
docker-compose up --build
```

El script `entrypoint.sh` automáticamente:
- ✅ Espera a que la base de datos esté lista
- ✅ Ejecuta las migraciones
- ✅ Recopila archivos estáticos
- ✅ Inicia el servidor Django

### 3. Crear superusuario (opcional)

En una nueva terminal:

```bash
docker-compose exec web python manage.py createsuperuser
```

### 4. Acceder a la aplicación

- **Frontend**: http://localhost:8000
- **Admin Panel**: http://localhost:8000/admin
- **API**: http://localhost:8000/api/

## 📝 Pruebas Rápidas

### Crear un usuario vía API

```bash
curl -X POST http://localhost:8000/api/usuarios/registro/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "testpass123",
    "password_confirm": "testpass123",
    "first_name": "Test",
    "last_name": "User"
  }'
```

### Listar publicaciones

```bash
curl http://localhost:8000/api/publicaciones/
```

### Listar eventos

```bash
curl http://localhost:8000/api/eventos/
```

## 🛑 Detener la aplicación

```bash
docker-compose down
```

Para eliminar también los volúmenes (datos de la base de datos):

```bash
docker-compose down -v
```

## 🔧 Solución de Problemas

### Error: "database is not ready"
Espera unos segundos más, la base de datos puede estar iniciando.

### Error: "port already in use"
Verifica que el puerto 8000 no esté en uso:
```bash
# Windows
netstat -ano | findstr :8000

# Linux/Mac
lsof -i :8000
```

### Reconstruir desde cero

```bash
docker-compose down -v
docker-compose up --build
```

## 📚 Documentación

Ver `README.md` para documentación completa.

