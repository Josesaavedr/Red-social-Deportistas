# 👋 ¡Bienvenido a Red Social Deportistas!

## 🎉 Cambios Realizados

Se han realizado mejoras importantes en la organización y documentación del proyecto:

### ✅ 1. Carpetas Renombradas

Las carpetas de microservicios ahora tienen nombres descriptivos:

```
services/
├── authentication/      (antes: sin cambios)
├── data-management/     (antes: service1)
├── notifications/       (antes: service2)
└── analytics/          (antes: service3)
```

### ✅ 2. Documentación Completa Creada

Se crearon **5 documentos** para explicar todo el proyecto:

| Documento | Para qué sirve |
|-----------|----------------|
| 📝 **README.md** | Instalación y uso básico |
| 📂 **GUIA_CARPETAS_Y_ARCHIVOS.md** | Qué hace cada carpeta y archivo |
| 🏗️ **ARQUITECTURA_DETALLADA.md** | Explicación técnica completa |
| 🗺️ **MAPA_SERVICIOS.md** | Diagramas y endpoints |
| 📋 **RESUMEN_CAMBIOS.md** | Resumen de cambios realizados |

---

## 🚀 Inicio Rápido

### Si es tu primera vez aquí:

1. **Lee primero:** [Guía de Inicio (README)](proyecto/README.md) (5 minutos)
   - Qué es el proyecto
   - Cómo instalarlo
   - Comandos básicos

2. **Luego lee:** [Guía de Archivos](GUIA_CARPETAS_Y_ARCHIVOS.md) (15 minutos)
   - Qué hace cada carpeta
   - Dónde encontrar cada cosa

3. **Para profundizar:** [Arquitectura Detallada](ARQUITECTURA_DETALLADA.md) (30 minutos)
   - Cómo funciona todo el sistema
   - Modelos de datos
   - Flujos de trabajo

---

## 📚 Guía de Documentación

### 🟢 Para Principiantes
**Objetivo:** Entender y ejecutar el proyecto

→ **README.md** → **GUIA_CARPETAS_Y_ARCHIVOS.md**

**Tiempo:** 20 minutos

---

### 🟡 Para Desarrolladores
**Objetivo:** Desarrollar nuevas funcionalidades

→ **README.md** → **ARQUITECTURA_DETALLADA.md** → **MAPA_SERVICIOS.md**

**Tiempo:** 1 hora

---

### 🔴 Para Presentaciones
**Objetivo:** Explicar el proyecto a otros

→ **RESUMEN_CAMBIOS.md** → **MAPA_SERVICIOS.md** → **GUIA_CARPETAS_Y_ARCHIVOS.md**

**Tiempo:** 45 minutos

---

## 🎯 ¿Qué Necesitas?

### "Quiero instalar el proyecto"
→ Lee **[Guía de Inicio (README)](proyecto/README.md)** - Sección "Instalación y Ejecución"

### "Quiero entender qué hace cada carpeta"
→ Lee **[GUIA_CARPETAS_Y_ARCHIVOS.md](GUIA_CARPETAS_Y_ARCHIVOS.md)**

### "Quiero ver los endpoints disponibles"
→ Lee **[MAPA_SERVICIOS.md](MAPA_SERVICIOS.md)** - Sección "Endpoints Principales"

### "Quiero entender cómo funciona todo"
→ Lee **[ARQUITECTURA_DETALLADA.md](ARQUITECTURA_DETALLADA.md)**

### "Quiero saber qué cambió"
→ Lee **[RESUMEN_CAMBIOS.md](RESUMEN_CAMBIOS.md)**

### "Quiero un índice completo"
→ Lee **[INDICE_DOCUMENTACION.md](INDICE_DOCUMENTACION.md)**

---

## 🏗️ Arquitectura en 30 Segundos

```
CLIENTE WEB
    ↓
DJANGO (Puerto 8000)
    ├── usuarios/          → Perfiles deportivos
    ├── publicaciones/     → Posts, likes, entrenamientos
    ├── eventos/           → Eventos deportivos
    └── seguimientos/      → Seguir a otros usuarios
    ↓
PostgreSQL (Puerto 5432)

MICROSERVICIOS (FastAPI)
    ├── authentication/    → Login JWT
    ├── data-management/   → Multi-DB (SQL, Mongo, Redis)
    ├── notifications/     → Notificaciones
    └── analytics/         → Métricas y análisis
```

---

## 📊 Servicios Renombrados

### 💾 data-management (antes service1)
**Qué hace:** Gestiona múltiples bases de datos

**Archivos:**
- `database_sql.py` - PostgreSQL/MySQL
- `database_mongo.py` - MongoDB
- `database_redis.py` - Redis (caché)

**Para qué sirve:**
- Caché de datos frecuentes
- Logs y métricas
- Estadísticas de rendimiento

---

### 🔔 notifications (antes service2)
**Qué hace:** Sistema de notificaciones (plantilla)

**Para qué sirve:**
- Notificaciones push
- Emails automáticos
- Alertas en tiempo real

---

### 📊 analytics (antes service3)
**Qué hace:** Análisis y métricas (plantilla)

**Para qué sirve:**
- Estadísticas deportivas
- Análisis de progreso
- Dashboards y reportes

---

## 🎓 Conceptos Clave

### Django Apps (Aplicaciones)
El proyecto tiene 4 apps principales:

1. **usuarios/** - Gestión de usuarios y perfiles
2. **publicaciones/** - Posts, likes, comentarios, entrenamientos
3. **eventos/** - Eventos deportivos
4. **seguimientos/** - Red social (seguir/seguidores)

### Microservicios (FastAPI)
Servicios independientes para funcionalidades específicas:

- **authentication** - Autenticación JWT
- **data-management** - Multi-base de datos
- **notifications** - Notificaciones
- **analytics** - Análisis

### API Gateway
Enrutador que dirige peticiones a los microservicios correctos.

---

## 🛠️ Comandos Esenciales

```bash
# Iniciar el proyecto
docker-compose up -d

# Ver logs
docker-compose logs -f web

# Ejecutar migraciones
docker-compose exec web python manage.py migrate

# Crear superusuario
docker-compose exec web python manage.py createsuperuser

# Detener el proyecto
docker-compose down
```

---

## 📖 Orden de Lectura Recomendado

### Lectura Completa (2 horas)

1. **[Guía de Inicio (README)](proyecto/README.md)** (5 min)
   - Instalación y configuración

2. **[RESUMEN_CAMBIOS.md](RESUMEN_CAMBIOS.md)** (10 min)
   - Qué cambió y por qué

3. **[GUIA_CARPETAS_Y_ARCHIVOS.md](GUIA_CARPETAS_Y_ARCHIVOS.md)** (20 min)
   - Estructura del proyecto

4. **[MAPA_SERVICIOS.md](MAPA_SERVICIOS.md)** (25 min)
   - Diagramas y endpoints

5. **[ARQUITECTURA_DETALLADA.md](ARQUITECTURA_DETALLADA.md)** (40 min)
   - Detalles técnicos completos

6. **[INDICE_DOCUMENTACION.md](INDICE_DOCUMENTACION.md)** (10 min)
   - Referencia de toda la documentación

---

## ✨ Beneficios de Esta Documentación

### Antes:
❌ Nombres genéricos (service1, service2, service3)  
❌ Sin documentación de arquitectura  
❌ Difícil de entender  

### Ahora:
✅ Nombres descriptivos y claros  
✅ Documentación completa y detallada  
✅ Fácil de explicar a otros  
✅ Preparado para presentaciones  
✅ Guía para nuevos desarrolladores  

---

## 🎯 Próximos Pasos

1. **Lee la documentación** según tu necesidad
2. **Instala el proyecto** siguiendo README.md
3. **Explora el código** usando las guías
4. **Desarrolla nuevas funcionalidades** con confianza

---

## 📞 Estructura de Soporte

Si tienes dudas sobre:

- **Instalación** → [Guía de Inicio (README)](proyecto/README.md)
- **Estructura** → GUIA_CARPETAS_Y_ARCHIVOS.md
- **Arquitectura** → ARQUITECTURA_DETALLADA.md
- **APIs** → MAPA_SERVICIOS.md
- **Cambios** → RESUMEN_CAMBIOS.md

---

**¡Disfruta explorando el proyecto! 🚀**

---

**Última actualización:** 2025-11-16  
**Versión:** 1.0
