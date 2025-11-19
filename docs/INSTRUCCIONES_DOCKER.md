# Instrucciones para ejecutar el proyecto con Docker

## Arquitectura del Proyecto

Este proyecto está estructurado con una arquitectura de microservicios que incluye:

### Componentes:

1. **Frontend** (Puerto 5000)
   - Aplicación Flask que sirve la interfaz de usuario
   - Se comunica con el API Gateway

2. **API Gateway** (Puerto 8000)
   - Punto de entrada único para todas las peticiones
   - Enruta las peticiones a los microservicios correspondientes
   - Implementado con FastAPI

3. **Microservicios** (Puertos 8001-8004):
   - **Authentication Service** (8001): Gestión de autenticación y usuarios
   - **Data Management Service** (8002): Gestión de datos de deportistas
   - **Notifications Service** (8003): Gestión de notificaciones
   - **Analytics Service** (8004): Análisis y métricas

4. **Base de Datos** (Puerto 5432)
   - PostgreSQL 15
   - Compartida por todos los microservicios

## Requisitos Previos

- Docker instalado
- Docker Compose instalado

## Comandos para ejecutar el proyecto

### 1. Construir y levantar todos los servicios

```bash
docker-compose up --build
```

Este comando:
- Construye las imágenes de todos los servicios
- Levanta todos los contenedores
- Muestra los logs en tiempo real

### 2. Levantar los servicios en segundo plano

```bash
docker-compose up -d
```

### 3. Ver los logs de todos los servicios

```bash
docker-compose logs -f
```

### 4. Ver los logs de un servicio específico

```bash
docker-compose logs -f frontend
docker-compose logs -f api-gateway
docker-compose logs -f authentication-service
docker-compose logs -f data-management-service
docker-compose logs -f notifications-service
docker-compose logs -f analytics-service
```

### 5. Detener todos los servicios

```bash
docker-compose down
```

### 6. Detener y eliminar volúmenes

```bash
docker-compose down -v
```

## Acceso a los servicios

Una vez que todos los servicios estén corriendo, puedes acceder a:

- **Frontend**: http://localhost:5000
- **API Gateway**: http://localhost:8000
- **API Gateway Docs**: http://localhost:8000/docs
- **Authentication Service**: http://localhost:8001
- **Data Management Service**: http://localhost:8002
- **Notifications Service**: http://localhost:8003
- **Analytics Service**: http://localhost:8004

## Verificar el estado de los servicios

### Health checks:

```bash
# API Gateway
curl http://localhost:8000/health

# Authentication Service
curl http://localhost:8001/health

# Data Management Service
curl http://localhost:8002/health

# Notifications Service
curl http://localhost:8003/health

# Analytics Service
curl http://localhost:8004/health
```

## Ejemplos de uso del API Gateway

### Obtener deportistas (a través del API Gateway):

```bash
curl http://localhost:8000/api/v1/data/api/v1/deportistas
```

### Login (a través del API Gateway):

```bash
curl -X POST http://localhost:8000/api/v1/auth/api/v1/login \
  -H "Content-Type: application/json" \
  -d '{"username": "test", "password": "test123"}'
```

### Obtener métricas (a través del API Gateway):

```bash
curl http://localhost:8000/api/v1/analytics/api/v1/metricas
```

## Solución de problemas

### Si un servicio no inicia correctamente:

1. Verificar los logs:
   ```bash
   docker-compose logs [nombre-del-servicio]
   ```

2. Reconstruir el servicio específico:
   ```bash
   docker-compose up --build [nombre-del-servicio]
   ```

3. Reiniciar todos los servicios:
   ```bash
   docker-compose restart
   ```

### Si hay problemas con la base de datos:

```bash
# Eliminar volúmenes y reiniciar
docker-compose down -v
docker-compose up --build
```

## Estructura de red

Todos los servicios están conectados a la red `deportistas_network`, lo que permite la comunicación entre contenedores usando sus nombres de servicio.

