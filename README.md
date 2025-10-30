# Plantilla del Proyecto del Seminario

| Código | Nombre | Correo |
|:---|:---|:---|
| 542378923 | jose fernady saavedra duran| jose.saavedra.9076@miremington.edu.co |
| 542378923 | narciso yunda yunda | narciso.yunda.7718@miremington.edu.co |

---

# 🏋️‍♂️ Red Social para Deportistas

Una **plataforma social diseñada para atletas y aficionados al deporte**, donde los usuarios pueden compartir logros, registrar entrenamientos, participar en eventos y conectarse con otros deportistas.  
Desarrollada con **Python**, **FastAPI**, **Flask**, y **Docker**, bajo una arquitectura de **microservicios escalable**.

---


---

## 🧩 Descripción del Proyecto

La **Red Social para Deportistas** tiene como objetivo ofrecer un espacio digital interactivo donde cada usuario pueda:

- Crear un perfil deportivo personal o de club.  
- Registrar sus actividades físicas y entrenamientos.  
- Compartir publicaciones, logros y experiencias.  
- Interactuar con otros usuarios mediante comentarios, reacciones y mensajes.  
- Participar o crear eventos deportivos (torneos, maratones, encuentros, etc.).

---

## ⚙️ Arquitectura del Sistema

El sistema está diseñado bajo el enfoque de **microservicios**, lo que permite una mayor escalabilidad, independencia de componentes y facilidad de mantenimiento.

### Estructura General

```
red-social-deportistas/
├── api-gateway/
│   ├── main.py
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── app.py
│   ├── templates/
│   │   ├── base.html
│   │   ├── index.html
│   │   └── perfil.html
│   └── static/
│       ├── style.css
│       └── scripts.js
├── services/
│   ├── authentication/
│   │   ├── main.py
│   │   ├── models.py
│   │   └── routers/auth.py
│   ├── actividades/
│   │   ├── main.py
│   │   ├── models.py
│   │   └── routers/actividades.py
│   ├── social/
│   │   ├── main.py
│   │   ├── models.py
│   │   └── routers/interacciones.py
│   └── eventos/
│       ├── main.py
│       ├── models.py
│       └── routers/eventos.py
├── docker-compose.yml
├── .env.example
└── README.md
```

---

## 🧠 Microservicios Implementados

| Microservicio | Descripción | Base de Datos |
|----------------|-------------|---------------|
| **Autenticación** | Registra y autentica usuarios y clubes deportivos. |SQLAlchemy |
| **Actividades** | Gestiona los entrenamientos, estadísticas y logros. |SQLAlchemy |
| **Social** | Permite publicaciones, comentarios, reacciones y mensajes. |SQLAlchemy |
| **Eventos** | Administra torneos, competencias y encuentros deportivos. | SQLAlchemy|

---

## 🚀 Tecnologías Utilizadas

- **Python 3.11+**
- **FastAPI** – desarrollo de APIs RESTful.
- **Flask** – frontend liviano.
- **Docker y Docker Compose** – contenerización y orquestación.
- **PostgreSQL**, **MongoDB** y **Redis** – bases de datos híbridas.
- **HTML, CSS y JavaScript** – interfaz de usuario.
- **Git y GitHub** – control de versiones.

---

## 🧭 Instalación y Ejecución

1. **Clonar el repositorio:**
   ```bash
   git clone https://github.com/Josesaavedr/Red-social-Deportistas.git
   cd red-social-deportistas
   ```

2. **Configurar variables de entorno:**
   ```bash
   cp .env.example .env
   ```
   Edita el archivo `.env` con las credenciales necesarias.

3. **Construir y ejecutar los servicios:**
   ```bash
   docker-compose up --build
   ```

4. **Acceder a la aplicación:**
   - Frontend: [http://localhost:5000](http://localhost:5000)
   - API Gateway: [http://localhost:8000](http://localhost:8000)

---

## 🧩 Características Clave

- 🔐 Registro e inicio de sesión de usuarios con roles (atleta, club).  
- 🏃‍♂️ Publicación y seguimiento de entrenamientos.  
- 💬 Interacción social: comentarios, likes y mensajes.  
- 🏆 Organización de eventos y competiciones.  
- 📊 Métricas deportivas personalizadas.  
- 🌐 Arquitectura basada en microservicios y contenedores.  

---

## 📅 Futuras Mejoras

- Implementación de chat en tiempo real.  
- Sistema de recomendaciones deportivas.  
- Integración con APIs de dispositivos fitness (Strava, Garmin, etc.).  
- Aplicación móvil con Flutter o React Native.  

---

## 📄 Licencia

Este proyecto se distribuye bajo la licencia **MIT**.  
Puedes usarlo, modificarlo y distribuirlo libremente, siempre que se otorgue el crédito correspondiente al autor.
