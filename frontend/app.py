# /frontend/app.py

from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from datetime import datetime
from threading import Lock
import os
import requests

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")

# Obtén la URL del API Gateway desde las variables de entorno.
API_GATEWAY_URL = os.getenv("API_GATEWAY_URL", "http://api-gateway:8000")

# Almacenamiento en memoria para publicaciones/eventos compartidos entre sesiones.
GLOBAL_PUBLICATIONS = []
GLOBAL_EVENTS = []
PUBLICATION_SEQUENCE = 1
EVENT_SEQUENCE = 1
PUBLICATION_LOCK = Lock()
EVENT_LOCK = Lock()


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


def get_profile_from_session(username: str) -> dict:
    profile_data = session.get('profile_data')
    if not profile_data:
        profile_data = get_default_profile(username)
        session['profile_data'] = profile_data
    return profile_data


def normalize_api_list(payload):
    if isinstance(payload, dict):
        data = payload.get("data")
        if isinstance(data, list):
            return data
    return payload if isinstance(payload, list) else []


def parse_event_date(value: str):
    if not value:
        return None
    try:
        return datetime.fromisoformat(value)
    except ValueError:
        for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%Y-%m-%d %H:%M"):
            try:
                return datetime.strptime(value, fmt)
            except ValueError:
                continue
    return None


def format_duration(seconds: int) -> str:
    total_seconds = max(int(seconds or 0), 0)
    hours, remainder = divmod(total_seconds, 3600)
    minutes, sec = divmod(remainder, 60)
    if hours:
        return f"{hours:02d}:{minutes:02d}:{sec:02d}"
    return f"{minutes:02d}:{sec:02d}"


def register_publication(data: dict, owner: str):
    global PUBLICATION_SEQUENCE
    publication = dict(data)
    publication.setdefault("likes", 0)
    publication.setdefault("liked_by", [])
    publication.setdefault("duracion", None)
    publication.setdefault("comments", [])
    publication["owner"] = owner
    with PUBLICATION_LOCK:
        publication["id"] = PUBLICATION_SEQUENCE
        PUBLICATION_SEQUENCE += 1
        GLOBAL_PUBLICATIONS.insert(0, publication)
    return publication


def register_event(data: dict, owner: str):
    global EVENT_SEQUENCE
    evento = dict(data)
    evento.setdefault("attendees", [])
    evento.setdefault("estado", "proximo")
    evento["owner"] = owner
    evento["attendees_count"] = len(evento["attendees"])
    with EVENT_LOCK:
        evento["id"] = EVENT_SEQUENCE
        EVENT_SEQUENCE += 1
        GLOBAL_EVENTS.insert(0, evento)
    return evento


def find_publication(pub_id: int):
    for pub in GLOBAL_PUBLICATIONS:
        if pub.get("id") == pub_id:
            return pub
    return None


def find_event(event_id: int):
    for evento in GLOBAL_EVENTS:
        if evento.get("id") == event_id:
            return evento
    return None


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
        payload = response.json() if response.status_code == 200 else []
    except Exception as e:
        print(f"Error al obtener publicaciones: {e}")
        payload = []

    remote_posts = normalize_api_list(payload)
    for post in remote_posts:
        post.setdefault("likes", 0)
        post.setdefault("comments", [])

    publicaciones_feed = list(GLOBAL_PUBLICATIONS) + remote_posts
    liked_posts = session.get('liked_publications', [])

    return render_template(
        "publicaciones/lista.html",
        publicaciones=publicaciones_feed,
        liked_posts=liked_posts,
    )

@app.route("/publicaciones/feed")
def feed_publicaciones():
    """Feed de publicaciones."""
    try:
        response = requests.get(f"{API_GATEWAY_URL}/api/v1/data/deportistas")
        payload = response.json() if response.status_code == 200 else []
    except Exception as e:
        print(f"Error al obtener feed: {e}")
        payload = []

    remote_posts = normalize_api_list(payload)
    publicaciones_feed = list(GLOBAL_PUBLICATIONS) + remote_posts

    return render_template("publicaciones/feed.html", publicaciones=publicaciones_feed)

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
            success = response.status_code == 200
        except Exception as e:
            print(f"Error al crear publicación: {e}")
            flash("Error al crear la publicación", "danger")
            success = False

        profile = get_profile_from_session(session.get('user_id')) if session.get('user_id') else get_default_profile("Invitado")
        owner = session.get('user_id', 'Invitado')
        user_post = {
            "titulo": publicacion_data.get("titulo") or "Publicación sin título",
            "contenido": publicacion_data.get("contenido") or "",
            "autor": profile.get("full_name") or owner,
            "deporte": profile.get("sport"),
            "imagen": profile.get("photo_url"),
            "fecha": datetime.utcnow().strftime("%Y-%m-%d %H:%M"),
            "likes": 0,
            "comentarios": 0,
            "es_mio": True,
        }
        register_publication(user_post, owner)
        flash("Publicación creada exitosamente" if success else "Publicación guardada localmente", "success")
        return redirect(url_for("lista_publicaciones"))

    return render_template("publicaciones/crear.html")


@app.post("/publicaciones/entrenamiento")
def crear_publicacion_entrenamiento():
    if 'user_id' not in session:
        return jsonify({"success": False, "message": "Debes iniciar sesión primero"}), 401

    payload = request.get_json(silent=True) or {}
    duracion = payload.get("duracion")

    try:
        duracion_segundos = max(int(duracion), 0)
    except (TypeError, ValueError):
        duracion_segundos = 0

    if duracion_segundos <= 0:
        return jsonify({"success": False, "message": "El entrenamiento debe tener al menos un segundo."}), 400

    deporte = (payload.get("deporte") or "Entrenamiento").strip()
    descripcion = (payload.get("descripcion") or "Sesión registrada desde el temporizador.").strip()
    sensacion = (payload.get("sensacion") or "Sin comentarios").strip()

    profile = get_profile_from_session(session.get('user_id'))
    formatted_duration = format_duration(duracion_segundos)
    contenido = f"Duración: {formatted_duration}\nDeporte: {deporte}\nSensación: {sensacion}\n\n{descripcion}"

    nueva_publicacion = {
        "titulo": f"Entrenamiento de {deporte}",
        "contenido": contenido,
        "autor": profile.get("full_name") or session.get('user_id'),
        "deporte": deporte,
        "imagen": profile.get("photo_url"),
        "fecha": datetime.utcnow().strftime("%Y-%m-%d %H:%M"),
        "likes": 0,
        "comentarios": 0,
        "es_mio": True,
        "duracion": formatted_duration,
        "tipo": "entrenamiento",
    }

    register_publication(nueva_publicacion, session.get('user_id', 'Invitado'))
    return jsonify({"success": True})

@app.route("/publicaciones/<int:id>")
def detalle_publicacion(id):
    """Detalle de una publicación."""
    # Aquí podrías hacer una llamada al API para obtener el detalle
    return render_template("publicaciones/detalle.html", publicacion_id=id)


@app.post("/publicaciones/<int:pub_id>/like")
def like_publicacion(pub_id: int):
    if 'user_id' not in session:
        return jsonify({"success": False, "message": "Debes iniciar sesión"}), 401

    publication = find_publication(pub_id)
    if not publication:
        return jsonify({"success": False, "message": "Publicación no encontrada"}), 404

    username = session.get('user_id')
    liked_posts = session.get('liked_publications', [])
    publication.setdefault("liked_by", [])

    if pub_id in liked_posts or username in publication["liked_by"]:
        return jsonify({"success": False, "message": "Ya te gusta esta publicación"}), 400

    publication["likes"] = (publication.get("likes") or 0) + 1
    publication["liked_by"].append(username)
    liked_posts.append(pub_id)
    session['liked_publications'] = liked_posts
    session.modified = True
    return jsonify({"success": True, "likes": publication["likes"]})


@app.post("/publicaciones/<int:pub_id>/comentarios")
def comentar_publicacion(pub_id: int):
    if 'user_id' not in session:
        return jsonify({"success": False, "message": "Debes iniciar sesión"}), 401

    publication = find_publication(pub_id)
    if not publication:
        return jsonify({"success": False, "message": "Publicación no encontrada"}), 404

    payload = request.get_json(silent=True) or {}
    comentario = (payload.get("comentario") or "").strip()
    if not comentario:
        return jsonify({"success": False, "message": "Escribe un comentario"}), 400

    comment = {
        "autor": session.get('user_id'),
        "perfil": get_profile_from_session(session.get('user_id')).get("photo_url"),
        "texto": comentario,
        "fecha": datetime.utcnow().strftime("%Y-%m-%d %H:%M"),
    }
    publication.setdefault("comments", []).append(comment)
    return jsonify({"success": True, "comment": comment, "total": len(publication["comments"])})

# ==================== EVENTOS ====================
@app.route("/eventos")
def lista_eventos():
    """Lista de eventos."""
    try:
        response = requests.get(f"{API_GATEWAY_URL}/api/v1/analytics/metricas")
        payload = response.json() if response.status_code == 200 else []
    except Exception as e:
        print(f"Error al obtener eventos: {e}")
        payload = []

    local_events = []
    for ev in GLOBAL_EVENTS:
        event_copy = dict(ev)
        event_copy.setdefault("attendees", [])
        event_copy["attendees_count"] = len(event_copy["attendees"])
        local_events.append(event_copy)

    remote_events = normalize_api_list(payload)
    for ev in remote_events:
        ev.setdefault("attendees_count", 0)

    eventos_feed = local_events + remote_events

    today = datetime.utcnow().date()
    annotated_events = []
    for ev in eventos_feed:
        event_copy = dict(ev)
        event_date = parse_event_date(event_copy.get("fecha"))
        if event_date:
            event_copy["fecha_legible"] = event_date.strftime("%d/%m/%Y")
            event_copy["estado"] = "proximo" if event_date.date() >= today else "pasado"
        else:
            event_copy["fecha_legible"] = event_copy.get("fecha", "Por definir")
            event_copy["estado"] = "sin_fecha"
        annotated_events.append(event_copy)
    eventos_feed = annotated_events

    filtro = request.args.get("filtro", "todos")

    def is_future(ev):
        event_date = parse_event_date(ev.get("fecha"))
        return event_date.date() >= today if event_date else False

    def is_past(ev):
        event_date = parse_event_date(ev.get("fecha"))
        return event_date.date() < today if event_date else False

    eventos_mios = [ev for ev in eventos_feed if ev.get("owner") == session.get('user_id') or ev.get("es_mio")]

    eventos_por_filtro = {
        "todos": eventos_feed,
        "proximos": [ev for ev in eventos_feed if is_future(ev)],
        "pasados": [ev for ev in eventos_feed if is_past(ev)],
        "mios": eventos_mios,
    }

    eventos_seleccionados = eventos_por_filtro.get(filtro, eventos_feed)
    counts = {clave: len(valor) for clave, valor in eventos_por_filtro.items()}

    return render_template(
        "eventos/lista.html",
        eventos=eventos_seleccionados,
        filtro=filtro,
        counts=counts,
        attending_events=session.get('attending_events', []),
    )

@app.route("/eventos/crear", methods=["GET", "POST"])
def crear_evento():
    """Crear un nuevo evento."""
    if request.method == "POST":
        evento_data = {
            "nombre": request.form.get("nombre"),
            "descripcion": request.form.get("descripcion"),
            "fecha": request.form.get("fecha"),
            "lugar": request.form.get("lugar") or "Por definir",
        }

        try:
            response = requests.post(
                f"{API_GATEWAY_URL}/api/v1/analytics/analizar",
                json=evento_data
            )
            success = response.status_code == 200
        except Exception as e:
            print(f"Error al crear evento: {e}")
            flash("Error al crear el evento", "danger")
            success = False

        owner = session.get('user_id', 'Invitado')
        user_event = {
            "nombre": evento_data.get("nombre") or "Evento deportivo",
            "descripcion": evento_data.get("descripcion") or "",
            "fecha": evento_data.get("fecha") or datetime.utcnow().strftime("%Y-%m-%d"),
            "lugar": evento_data.get("lugar"),
            "organizador": owner,
            "es_mio": True,
            "attendees": [],
        }
        register_event(user_event, owner)
        flash("Evento creado exitosamente" if success else "Evento guardado localmente", "success")
        return redirect(url_for("lista_eventos"))

    return render_template("eventos/crear.html")

@app.route("/eventos/<int:id>")
def detalle_evento(id):
    """Detalle de un evento."""
    return render_template("eventos/detalle.html", evento_id=id)


@app.post("/eventos/<int:event_id>/asistir")
def asistir_evento(event_id: int):
    if 'user_id' not in session:
        return jsonify({"success": False, "message": "Debes iniciar sesión"}), 401

    evento = find_event(event_id)
    if not evento:
        return jsonify({"success": False, "message": "Evento no encontrado"}), 404

    username = session.get('user_id')
    attending_events = session.get('attending_events', [])
    evento.setdefault("attendees", [])

    if event_id in attending_events:
        attending_events.remove(event_id)
        if username in evento["attendees"]:
            evento["attendees"].remove(username)
        attending = False
    else:
        attending_events.append(event_id)
        if username not in evento["attendees"]:
            evento["attendees"].append(username)
        attending = True

    evento["attendees_count"] = len(evento["attendees"])
    session['attending_events'] = attending_events
    session.modified = True
    return jsonify({
        "success": True,
        "attending": attending,
        "attendees": evento["attendees_count"],
    })

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
    user_publications = [pub for pub in GLOBAL_PUBLICATIONS if pub.get("owner") == username]
    user_events = [ev for ev in GLOBAL_EVENTS if ev.get("owner") == username]

    stats = {
        "publicaciones": len(user_publications),
        "eventos": len(user_events),
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
