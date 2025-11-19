# Guía Completa - Red Social Deportistas con Microservicios

## 📋 Índice
1. [Arquitectura](#arquitectura)
2. [Componentes](#componentes)
3. [Instalación y Ejecución](#instalación-y-ejecución)
4. [Verificación](#verificación)
5. [Uso de la API](#uso-de-la-api)
6. [Desarrollo](#desarrollo)

---

## 🏗️ Arquitectura

El proyecto está estructurado con una arquitectura de microservicios moderna:

```
Cliente (Navegador)
    ↓
Frontend (Flask - Puerto 5000)
    ↓
API Gateway (FastAPI - Puerto 8000)
    ↓
┌─────────────┬──────────────┬──────────────┬──────────────┐
│ Auth (8001) │ Data (8002)  │ Notif (8003) │ Analy (8004) │
└─────────────┴──────────────┴──────────────┴──────────────┘
                        ↓
              PostgreSQL (Puerto 5432)
```

---

## 🔧 Componentes

### 1. Frontend (Puerto 5000)
- **Tecnología**: Flask
- **Función**: Interfaz de usuario
- **Ubicación**: `./frontend/`

### 2. API Gateway (Puerto 8000)
- **Tecnología**: FastAPI
- **Función**: Punto de entrada único, enrutamiento de peticiones
- **Ubicación**: `./api-gateway/`
- **Documentación**: http://localhost:8000/docs

### 3. Microservicios

#### Authentication Service (Puerto 8001)
- **Endpoints**:
  - `POST /api/v1/login` - Iniciar sesión
  - `POST /api/v1/register` - Registrar usuario
  - `POST /api/v1/logout` - Cerrar sesión
  - `GET /api/v1/verify` - Verificar token

#### Data Management Service (Puerto 8002)
- **Endpoints**:
  - `GET /api/v1/deportistas` - Listar deportistas
  - `POST /api/v1/deportistas` - Crear deportista
  - `GET /api/v1/estadisticas` - Obtener estadísticas

#### Notifications Service (Puerto 8003)
- **Endpoints**:
  - `GET /api/v1/notificaciones` - Listar notificaciones
  - `POST /api/v1/notificaciones` - Crear notificación
  - `POST /api/v1/enviar` - Enviar notificación

#### Analytics Service (Puerto 8004)
- **Endpoints**:
  - `GET /api/v1/metricas` - Obtener métricas
  - `GET /api/v1/reportes` - Listar reportes
  - `POST /api/v1/analizar` - Analizar datos

### 4. Base de Datos (Puerto 5432)
- **Tecnología**: PostgreSQL 15
- **Nombre**: deportistas_db
- **Usuario**: deportistas_user

---

## 🚀 Instalación y Ejecución

### Requisitos Previos
- Docker
- Docker Compose

### Pasos

1. **Clonar el repositorio** (si aplica)
   ```bash
   git clone <url-del-repositorio>
   cd Red-social-Deportistas
   ```

2. **Construir y levantar todos los servicios**
   ```bash
   docker-compose up --build
   ```

3. **Levantar en segundo plano**
   ```bash
   docker-compose up -d
   ```

4. **Ver logs**
   ```bash
   # Todos los servicios
   docker-compose logs -f
   
   # Un servicio específico
   docker-compose logs -f api-gateway
   ```

5. **Detener servicios**
   ```bash
   docker-compose down
   ```

---

## ✅ Verificación

### Opción 1: Script Automático
```bash
./test_services.sh
```

### Opción 2: Manual

```bash
# API Gateway
curl http://localhost:8000/health

# Frontend
curl http://localhost:5000

# Authentication Service
curl http://localhost:8001/health

# Data Management Service
curl http://localhost:8002/health

# Notifications Service
curl http://localhost:8003/health

# Analytics Service
curl http://localhost:8004/health
```

---

## 🔌 Uso de la API

### Acceso Directo a Microservicios

```bash
# Obtener deportistas
curl http://localhost:8002/api/v1/deportistas

# Login
curl -X POST http://localhost:8001/api/v1/login \
  -H "Content-Type: application/json" \
  -d '{"username": "test", "password": "test123"}'
```

### Acceso a través del API Gateway

```bash
# Formato: http://localhost:8000/api/v1/{servicio}/{ruta}

# Obtener deportistas
curl http://localhost:8000/api/v1/data/api/v1/deportistas

# Login
curl -X POST http://localhost:8000/api/v1/auth/api/v1/login \
  -H "Content-Type: application/json" \
  -d '{"username": "test", "password": "test123"}'

# Obtener métricas
curl http://localhost:8000/api/v1/analytics/api/v1/metricas
```

---

## 👨‍💻 Desarrollo

### Estructura de Archivos

```
Red-social-Deportistas/
├── docker-compose.yml          # Configuración de todos los servicios
├── .env.example                # Variables de entorno de ejemplo
├── test_services.sh            # Script de verificación
│
├── frontend/                   # Frontend Flask
│   ├── Dockerfile
│   ├── app.py
│   ├── requirements.txt
│   └── templates/
│
├── api-gateway/                # API Gateway
│   ├── Dockerfile
│   ├── main.py
│   └── requirements.txt
│
└── services/                   # Microservicios
    ├── authentication/
    │   ├── Dockerfile
    │   ├── main.py
    │   └── requirements.txt
    ├── data-management/
    ├── notifications/
    └── analytics/
```

### Agregar Nuevos Endpoints

1. Editar el archivo `main.py` del microservicio correspondiente
2. Agregar el nuevo endpoint usando FastAPI
3. Reconstruir el servicio: `docker-compose up --build [nombre-servicio]`

### Ver Documentación Interactiva

Cada microservicio FastAPI tiene documentación automática:
- http://localhost:8000/docs (API Gateway)
- http://localhost:8001/docs (Authentication)
- http://localhost:8002/docs (Data Management)
- http://localhost:8003/docs (Notifications)
- http://localhost:8004/docs (Analytics)

---

## 📚 Documentación Adicional

- `INSTRUCCIONES_DOCKER.md` - Instrucciones detalladas de Docker
- `RESUMEN_ARQUITECTURA.md` - Resumen de la arquitectura
- Ver diagrama de arquitectura en el navegador

---

## 🎯 Próximos Pasos

1. Implementar autenticación real con JWT
2. Conectar microservicios a la base de datos PostgreSQL
3. Agregar validación de datos con Pydantic
4. Implementar tests unitarios
5. Agregar logging y monitoreo
6. Configurar CI/CD

