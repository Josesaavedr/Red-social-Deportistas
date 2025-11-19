# /frontend/app.py

from flask import Flask, render_template, request, redirect, url_for, session, flash
from datetime import datetime
import os
import requests

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")

# Obtén la URL del API Gateway desde las variables de entorno.
API_GATEWAY_URL = os.getenv("API_GATEWAY_URL", "http://api-gateway:8000")

# ==================== Helpers ====================
def get_default_profile(username: str) -> dict:
    """Datos base para mostrar un perfil completo aunque no exista personalización."""
    nice_name = username.capitalize() if username else "Deportista"
    return {
        "full_name": nice_name,
        "headline": "Apasionado del deporte y la vida activa",
        "sport": "Multideporte",
        "level": "Aficionado",
        "location": "Ciudad Global",
        "bio": "Comparte tus logros, registra tus entrenamientos y conecta con otros atletas.",
        "photo_url": "https://images.unsplash.com/photo-1521412644187-c49fa049e84d?auto=format&fit=crop&w=400&q=60",
        "cover_url": "https://images.unsplash.com/photo-1500530855697-b586d89ba3ee?auto=format&fit=crop&w=1200&q=60",
        "website": "",
        "instagram": "",
        "twitter": "",
        "interests": ["Resistencia", "Trabajo en equipo", "Salud"]
    }


def store_user_item(key: str, item: dict):
    """Guarda listas ligeras (publicaciones/eventos) en sesión."""
    items = session.get(key, [])
    items.insert(0, item)
    session[key] = items
    session.modified = True


def get_profile_from_session(username: str) -> dict:
    profile_data = session.get('profile_data')
    if not profile_data:
        profile_data = get_default_profile(username)
        session['profile_data'] = profile_data
    return profile_data


# ==================== PÁGINA PRINCIPAL ====================
@app.route("/")
def index():
    """Página de inicio."""
    return render_template("index.html")

# ==================== PUBLICACIONES ====================
@app.route("/publicaciones")
def lista_publicaciones():
    """Lista de publicaciones."""
    try:
        # Obtener publicaciones desde el microservicio de data management
        response = requests.get(f"{API_GATEWAY_URL}/api/v1/data/deportistas")
        publicaciones = response.json() if response.status_code == 200 else []
    except Exception as e:
        print(f"Error al obtener publicaciones: {e}")
        publicaciones = []

    return render_template("publicaciones/lista.html", publicaciones=publicaciones)

@app.route("/publicaciones/feed")
def feed_publicaciones():
    """Feed de publicaciones."""
    try:
        response = requests.get(f"{API_GATEWAY_URL}/api/v1/data/deportistas")
        publicaciones = response.json() if response.status_code == 200 else []
    except Exception as e:
        print(f"Error al obtener feed: {e}")
        publicaciones = []

    return render_template("publicaciones/feed.html", publicaciones=publicaciones)

@app.route("/publicaciones/crear", methods=["GET", "POST"])
def crear_publicacion():
    """Crear una nueva publicación."""
    if request.method == "POST":
        publicacion_data = {
            "titulo": request.form.get("titulo"),
            "contenido": request.form.get("contenido"),
        }

        try:
            response = requests.post(
                f"{API_GATEWAY_URL}/api/v1/data/deportistas",
                json=publicacion_data
            )
            if response.status_code == 200:
                store_user_item("my_publications", {
                    "titulo": publicacion_data.get("titulo") or "Publicación sin título",
                    "contenido": publicacion_data.get("contenido") or "",
                    "autor": session.get('user_id', 'Invitado'),
                    "fecha": datetime.utcnow().strftime("%d/%m/%Y %H:%M")
                })
                flash("Publicación creada exitosamente", "success")
                return redirect(url_for("lista_publicaciones"))
        except Exception as e:
            print(f"Error al crear publicación: {e}")
            flash("Error al crear la publicación", "danger")

    return render_template("publicaciones/crear.html")

@app.route("/publicaciones/<int:id>")
def detalle_publicacion(id):
    """Detalle de una publicación."""
    # Aquí podrías hacer una llamada al API para obtener el detalle
    return render_template("publicaciones/detalle.html", publicacion_id=id)

# ==================== EVENTOS ====================
@app.route("/eventos")
def lista_eventos():
    """Lista de eventos."""
    try:
        response = requests.get(f"{API_GATEWAY_URL}/api/v1/analytics/metricas")
        eventos = response.json() if response.status_code == 200 else []
    except Exception as e:
        print(f"Error al obtener eventos: {e}")
        eventos = []

    return render_template("eventos/lista.html", eventos=eventos)

@app.route("/eventos/crear", methods=["GET", "POST"])
def crear_evento():
    """Crear un nuevo evento."""
    if request.method == "POST":
        evento_data = {
            "nombre": request.form.get("nombre"),
            "descripcion": request.form.get("descripcion"),
            "fecha": request.form.get("fecha"),
        }

        try:
            response = requests.post(
                f"{API_GATEWAY_URL}/api/v1/analytics/analizar",
                json=evento_data
            )
            if response.status_code == 200:
                store_user_item("my_events", {
                    "nombre": evento_data.get("nombre") or "Evento deportivo",
                    "descripcion": evento_data.get("descripcion") or "",
                    "fecha": evento_data.get("fecha") or datetime.utcnow().strftime("%Y-%m-%d"),
                    "organizador": session.get('user_id', 'Invitado')
                })
                flash("Evento creado exitosamente", "success")
                return redirect(url_for("lista_eventos"))
        except Exception as e:
            print(f"Error al crear evento: {e}")
            flash("Error al crear el evento", "danger")

    return render_template("eventos/crear.html")

@app.route("/eventos/<int:id>")
def detalle_evento(id):
    """Detalle de un evento."""
    return render_template("eventos/detalle.html", evento_id=id)

# ==================== USUARIOS ====================
@app.route("/login", methods=["GET", "POST"])
def login():
    """Iniciar sesión."""
    if request.method == "POST":
        credentials = {
            "username": request.form.get("username"),
            "password": request.form.get("password"),
        }

        try:
            response = requests.post(
                f"{API_GATEWAY_URL}/api/v1/auth/login",
                json=credentials
            )
            if response.status_code == 200:
                data = response.json()
                session['user_id'] = credentials['username']
                session['token'] = data.get('token', '')
                flash("Inicio de sesión exitoso", "success")
                return redirect(url_for("index"))
            else:
                flash("Credenciales inválidas", "danger")
        except Exception as e:
            print(f"Error al iniciar sesión: {e}")
            flash("Error al conectar con el servidor", "danger")

    return render_template("usuarios/login.html")

@app.route("/registro", methods=["GET", "POST"])
def registro():
    """Registrar un nuevo usuario."""
    if request.method == "POST":
        user_data = {
            "username": request.form.get("username"),
            "email": request.form.get("email"),
            "password": request.form.get("password"),
        }

        try:
            response = requests.post(
                f"{API_GATEWAY_URL}/api/v1/auth/register",
                json=user_data
            )
            if response.status_code == 200:
                flash("Registro exitoso. Por favor inicia sesión.", "success")
                return redirect(url_for("login"))
            else:
                flash("Error al registrar usuario", "danger")
        except Exception as e:
            print(f"Error al registrar: {e}")
            flash("Error al conectar con el servidor", "danger")

    return render_template("usuarios/registro.html")

@app.route("/logout")
def logout():
    """Cerrar sesión."""
    session.clear()
    flash("Sesión cerrada exitosamente", "success")
    return redirect(url_for("index"))

@app.route("/perfil")
def perfil_usuario():
    """Perfil del usuario."""
    if 'user_id' not in session:
        flash("Debes iniciar sesión primero", "warning")
        return redirect(url_for("login"))

    username = session.get('user_id')
    profile_data = get_profile_from_session(username)
    user_publications = session.get('my_publications', [])
    user_events = session.get('my_events', [])

    stats = {
        "publicaciones": len(user_publications),
        "eventos": len(user_events),
        "seguidores": max(12, len(user_publications) * 3),
    }

    return render_template(
        "usuarios/perfil.html",
        username=username,
        profile=profile_data,
        publicaciones=user_publications,
        eventos=user_events,
        stats=stats,
    )

@app.route("/perfil/editar", methods=["GET", "POST"])
def editar_perfil():
    """Editar perfil del usuario."""
    if 'user_id' not in session:
        flash("Debes iniciar sesión primero", "warning")
        return redirect(url_for("login"))

    username = session.get('user_id')
    profile_data = get_profile_from_session(username)

    if request.method == "POST":
        profile_data = {
            "full_name": request.form.get("full_name") or profile_data.get("full_name"),
            "headline": request.form.get("headline") or profile_data.get("headline"),
            "sport": request.form.get("sport") or profile_data.get("sport"),
            "level": request.form.get("level") or profile_data.get("level"),
            "location": request.form.get("location") or profile_data.get("location"),
            "bio": request.form.get("bio") or profile_data.get("bio"),
            "photo_url": request.form.get("photo_url") or profile_data.get("photo_url"),
            "cover_url": request.form.get("cover_url") or profile_data.get("cover_url"),
            "website": request.form.get("website") or "",
            "instagram": request.form.get("instagram") or "",
            "twitter": request.form.get("twitter") or "",
            "interests": [tag.strip() for tag in request.form.get("interests", "").split(",") if tag.strip()] or profile_data.get("interests", []),
        }
        session['profile_data'] = profile_data
        session.modified = True
        flash("Perfil actualizado exitosamente", "success")
        return redirect(url_for("perfil_usuario"))

    return render_template("usuarios/editar_perfil.html", profile=profile_data)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
