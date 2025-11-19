# Resumen de la Arquitectura de Microservicios

## ✅ Cambios Realizados

### 1. Docker Compose Actualizado

El archivo `docker-compose.yml` ahora incluye **7 servicios**:

#### Base de Datos
- **deportistas_db** (PostgreSQL 15) - Puerto 5432

#### Frontend
- **frontend** (Flask) - Puerto 5000
  - Interfaz de usuario
  - Se comunica con el API Gateway

#### API Gateway
- **api-gateway** (FastAPI) - Puerto 8000
  - Punto de entrada único
  - Enruta peticiones a los microservicios
  - Endpoints: GET, POST, PUT, DELETE

#### Microservicios (4)
1. **authentication-service** (FastAPI) - Puerto 8001
   - Login, registro, logout, verificación de tokens
   
2. **data-management-service** (FastAPI) - Puerto 8002
   - Gestión de deportistas y estadísticas
   
3. **notifications-service** (FastAPI) - Puerto 8003
   - Creación y envío de notificaciones
   
4. **analytics-service** (FastAPI) - Puerto 8004
   - Métricas, reportes y análisis de datos

### 2. Configuración de Red

Todos los servicios están conectados a la red `deportistas_network`, permitiendo comunicación interna entre contenedores.

### 3. Archivos Actualizados

#### API Gateway (`api-gateway/main.py`)
- ✅ Configurado con los 4 microservicios
- ✅ Rutas genéricas para GET, POST, PUT, DELETE
- ✅ Variables de entorno para URLs de servicios

#### Microservicios
Cada microservicio tiene:
- ✅ `Dockerfile` configurado con el puerto correcto
- ✅ `main.py` con endpoints de ejemplo
- ✅ `requirements.txt` con dependencias necesarias
- ✅ Endpoint `/health` para health checks
- ✅ Endpoint `/` con información del servicio

### 4. Flujo de Comunicación

```
Usuario → Frontend (5000) → API Gateway (8000) → Microservicios (8001-8004) → PostgreSQL (5432)
```

## 📋 Estructura de Puertos

| Servicio | Puerto | Tecnología |
|----------|--------|------------|
| Frontend | 5000 | Flask |
| API Gateway | 8000 | FastAPI |
| Authentication | 8001 | FastAPI |
| Data Management | 8002 | FastAPI |
| Notifications | 8003 | FastAPI |
| Analytics | 8004 | FastAPI |
| PostgreSQL | 5432 | PostgreSQL 15 |

## 🚀 Cómo Ejecutar

```bash
# Construir y levantar todos los servicios
docker-compose up --build

# En segundo plano
docker-compose up -d

# Ver logs
docker-compose logs -f

# Detener
docker-compose down
```

## 🔍 Verificar Servicios

```bash
# Health checks
curl http://localhost:8000/health  # API Gateway
curl http://localhost:8001/health  # Authentication
curl http://localhost:8002/health  # Data Management
curl http://localhost:8003/health  # Notifications
curl http://localhost:8004/health  # Analytics
```

## 📚 Documentación API

- API Gateway: http://localhost:8000/docs
- Authentication: http://localhost:8001/docs
- Data Management: http://localhost:8002/docs
- Notifications: http://localhost:8003/docs
- Analytics: http://localhost:8004/docs

## 🎯 Endpoints de Ejemplo

### Authentication Service (8001)
- POST `/api/v1/login` - Iniciar sesión
- POST `/api/v1/register` - Registrar usuario
- POST `/api/v1/logout` - Cerrar sesión
- GET `/api/v1/verify?token=xxx` - Verificar token

### Data Management Service (8002)
- GET `/api/v1/deportistas` - Listar deportistas
- POST `/api/v1/deportistas` - Crear deportista
- GET `/api/v1/estadisticas` - Obtener estadísticas

### Notifications Service (8003)
- GET `/api/v1/notificaciones` - Listar notificaciones
- POST `/api/v1/notificaciones` - Crear notificación
- POST `/api/v1/enviar` - Enviar notificación

### Analytics Service (8004)
- GET `/api/v1/metricas` - Obtener métricas
- GET `/api/v1/reportes` - Listar reportes
- POST `/api/v1/analizar` - Analizar datos

## 🔗 Uso a través del API Gateway

Para acceder a los microservicios a través del API Gateway:

```bash
# Formato: http://localhost:8000/api/v1/{servicio}/{ruta}

# Ejemplo: Login
curl -X POST http://localhost:8000/api/v1/auth/api/v1/login \
  -H "Content-Type: application/json" \
  -d '{"username": "test", "password": "test123"}'

# Ejemplo: Obtener deportistas
curl http://localhost:8000/api/v1/data/api/v1/deportistas

# Ejemplo: Obtener métricas
curl http://localhost:8000/api/v1/analytics/api/v1/metricas
```

## ✨ Ventajas de esta Arquitectura

1. **Escalabilidad**: Cada microservicio puede escalarse independientemente
2. **Mantenibilidad**: Código organizado y separado por responsabilidades
3. **Resiliencia**: Si un servicio falla, los demás siguen funcionando
4. **Desarrollo independiente**: Equipos pueden trabajar en diferentes servicios
5. **Tecnología flexible**: Cada servicio puede usar diferentes tecnologías
6. **Punto de entrada único**: El API Gateway centraliza el acceso

