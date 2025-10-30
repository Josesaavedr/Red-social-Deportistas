# /frontend/app.py

from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_wtf.csrf import CSRFProtect
from datetime import datetime
import requests
import os
from common.config import settings # Importa la configuración global
from functools import wraps
from urllib.parse import urlparse, urljoin

app = Flask(__name__)
# Es crucial para usar sesiones de forma segura.
# En producción, esto debería ser una cadena larga y aleatoria.
app.secret_key = os.getenv("FLASK_SECRET_KEY", "super-secret-key-for-dev")

# --- Mejoras de Seguridad y Configuración ---
csrf = CSRFProtect(app) # Inicializa la protección CSRF

ACTIVITIES_PER_PAGE = 9

@app.route("/")
def index():
    """
    Filtro personalizado de Jinja2 para formatear objetos datetime.
    Asume que el valor de entrada es una cadena ISO 8601.
    """
    def format_datetime_filter(value, format="%d/%m/%Y %H:%M"):
        if not value:
            return ""
        try:
            dt_object = datetime.fromisoformat(value)
            return dt_object.strftime(format)
        except ValueError:
            return value # Devuelve el valor original si no se puede parsear
    app.jinja_env.filters['datetimeformat'] = format_datetime_filter


    page = request.args.get('page', 1, type=int)
    skip = (page - 1) * ACTIVITIES_PER_PAGE

    activities = []
    total_activities = 0

    try:
        # Usamos la función centralizada para hacer la petición
        success, data, status_code = api_request("get", f"api/v1/activities/count")
        if success:
            total_activities = data.get('total', 0)
            if total_activities > 0:
                success_act, activities_data, _ = api_request("get", f"api/v1/activities/?skip={skip}&limit={ACTIVITIES_PER_PAGE}")
                if success_act:
                    activities = activities_data
    except Exception as e:
        print(f"Error al obtener actividades: {e}")
        activities = []
        total_activities = 0

    total_pages = (total_activities + ACTIVITIES_PER_PAGE - 1) // ACTIVITIES_PER_PAGE

    # Pasa los datos a la plantilla para renderizarlos.
    return render_template("index.html", title="Inicio", activities=activities, page=page, total_pages=total_pages)

# --- Funciones de Utilidad y Seguridad ---

def is_safe_url(target):
    """Valida que una URL de redirección sea segura y pertenezca al mismo host."""
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and ref_url.netloc == test_url.netloc

def login_required(f):
    """
    Decorador para proteger rutas que requieren autenticación.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'token' not in session:
            flash("Debes iniciar sesión para ver esta página.", "warning")
            # Valida la URL 'next' para evitar redirecciones abiertas
            next_url = request.url
            if not is_safe_url(next_url):
                next_url = url_for('index')
            return redirect(url_for('login', next=next_url))
        return f(*args, **kwargs)
    return decorated_function

def get_auth_headers():
    """Obtiene las cabeceras de autenticación si el usuario ha iniciado sesión."""
    if 'token' not in session:
        return {}
    return {"Authorization": f"Bearer {session.get('token')}"}

def api_request(method, endpoint, json=None, data=None):
    """Función centralizada para realizar peticiones al API Gateway."""
    url = f"{settings.API_GATEWAY_URL}/{endpoint}"
    headers = get_auth_headers()
    
    try:
        response = requests.request(method, url, headers=headers, json=json, data=data, timeout=10)
        response.raise_for_status() # Lanza HTTPError para respuestas 4xx/5xx
        
        # Manejar respuestas sin contenido (ej. 204 No Content)
        if response.status_code == 204:
            return True, None, 204

        return True, response.json(), response.status_code

    except requests.exceptions.HTTPError as e:
        # El error viene del API Gateway (ej. 401, 403, 404, 409)
        error_details = "Error desconocido."
        try:
            # Intenta obtener el detalle del error desde la respuesta JSON
            error_details = e.response.json().get("detail", error_details)
        except (ValueError, AttributeError):
            error_details = e.response.text
        print(f"Error HTTP {e.response.status_code} en {method.upper()} {url}: {error_details}")
        return False, {"detail": error_details}, e.response.status_code
    except requests.exceptions.RequestException as e:
        # Error de conexión, timeout, etc.
        print(f"Error de conexión en {method.upper()} {url}: {e}")
        return False, {"detail": "No se pudo conectar con el servidor. Inténtalo más tarde."}, 503


@app.route("/new-item", methods=["GET", "POST"])
def new_item():
    """Ruta para crear un nuevo ítem."""
    if request.method == "POST":
        # Recoge los datos del formulario.
        title = request.form.get("title")
        content = request.form.get("content")

        # Validación básica de los datos del formulario
        if not title or not content:
            flash("Error: Título y Detalles son requeridos.", "danger")
            return redirect(url_for('new_item'))

        activity_data = {"title": title, "content": content}
        
        success, data, status_code = api_request("post", "api/v1/activities/", json=activity_data)

        if success:
            flash("¡Actividad registrada con éxito!", "success")
            # Redirige a la página de detalles de la nueva actividad
            return redirect(url_for("activity_detail", activity_id=data['id']))
        else:
            flash(f"Error al registrar la actividad: {data.get('detail')}", "danger")
            return redirect(url_for('new_item'))

    return render_template("form.html", title="Registrar Nueva Actividad")

@app.route("/delete-activity/<int:activity_id>", methods=["POST"])
@login_required
def delete_activity(activity_id):
    """Ruta para eliminar una actividad."""
    success, data, status_code = api_request("delete", f"api/v1/activities/{activity_id}")

    if success:
        flash("Actividad eliminada correctamente.", "success")
        return redirect(url_for("index"))
    else:
        flash(f"Error al eliminar la actividad: {data.get('detail')}", "danger")
        return redirect(request.referrer or url_for('index'))
@app.route("/activity/<int:activity_id>")
def activity_detail(activity_id):
    """Ruta para ver los detalles de una actividad específica."""
    activity, comments = None, []
    try:
        # 1. Obtener los detalles de la actividad
        headers = get_auth_headers() if 'token' in session else {}
        success_act, activity_data, _ = api_request("get", f"api/v1/activities/{activity_id}")
        if not success_act:
            return render_template("error.html", message=activity_data.get('detail', 'Actividad no encontrada.')), 404
        activity = activity_data

        # 2. Obtener los comentarios de la actividad
        success_com, comments_data, _ = api_request("get", f"api/v1/activities/{activity_id}/comments")
        if success_com:
            comments = comments_data

    except requests.exceptions.RequestException as e:
        print(f"Error al obtener los detalles de la actividad: {e}")
        return render_template("error.html", message="Error al cargar la actividad."), 500

    return render_template("activity_detail.html", title=activity.get('title', 'Detalle de Actividad'), activity=activity, comments=comments)

@app.route("/activity/<int:activity_id>/comment", methods=["POST"])
@login_required
def add_comment(activity_id):
    """Ruta para añadir un nuevo comentario a una actividad."""
    content = request.form.get("content")
    if not content:
        flash("El contenido del comentario es requerido.", "warning")
        return redirect(url_for('activity_detail', activity_id=activity_id))

    success, data, _ = api_request("post", f"api/v1/activities/{activity_id}/comments", json={"content": content})
    if success:
        flash("Comentario añadido.", "success")
    else:
        flash(f"Error al publicar el comentario: {data.get('detail')}", "danger")

    return redirect(url_for('activity_detail', activity_id=activity_id))

@app.route("/edit-activity/<int:activity_id>", methods=["GET", "POST"])
@login_required
def edit_activity(activity_id):
    """Ruta para mostrar el formulario de edición y procesar la actualización."""
    if request.method == "POST":
        # Procesa el formulario enviado
        updated_data = {
            "title": request.form.get("title"),
            "content": request.form.get("content")
        }

        success, data, _ = api_request("put", f"api/v1/activities/{activity_id}", json=updated_data)

        if success:
            flash("Actividad actualizada correctamente.", "success")
            return redirect(url_for('activity_detail', activity_id=activity_id))
        else:
            flash(f"Error al actualizar la actividad: {data.get('detail')}", "danger")
            return redirect(url_for('edit_activity', activity_id=activity_id))

    # Método GET: Muestra el formulario de edición
    success, activity, status_code = api_request("get", f"api/v1/activities/{activity_id}")
    if not success:
        flash(f"No se pudo cargar la actividad para editar: {activity.get('detail')}", "danger")
        return redirect(url_for('index'))

    return render_template("edit_activity.html", activity=activity)

@app.route("/like-activity/<int:activity_id>", methods=["POST"]) # Cambiado a POST para enviar user_id
@login_required
def like_activity(activity_id):
    """Ruta para dar 'Me gusta' a una actividad."""
    success, data, status_code = api_request("post", f"api/v1/activities/{activity_id}/like")
    
    if success:
        flash("¡Gracias por tu 'Me gusta'!", "success")
    elif status_code == 409: # Conflicto
        flash("Ya has indicado que te gusta esta actividad.", "info")
    else:
        flash(f"No se pudo registrar tu 'Me gusta': {data.get('detail')}", "danger")
    # Redirige al usuario a la página desde la que vino
    return redirect(request.referrer or url_for('index'))

@app.route("/unlike-activity/<int:activity_id>", methods=["POST"])
@login_required
def unlike_activity(activity_id):
    """Ruta para quitar 'Me gusta' a una actividad."""
    success, data, status_code = api_request("delete", f"api/v1/activities/{activity_id}/like")

    if success:
        flash("Has quitado tu 'Me gusta'.", "success")
    elif status_code == 404:
        flash("No habías indicado que te gusta esta actividad.", "info")
    else:
        flash(f"No se pudo quitar tu 'Me gusta': {data.get('detail')}", "danger")
    return redirect(request.referrer or url_for('index'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Ruta para iniciar sesión."""
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        # El servicio de usuarios espera los datos en formato 'form-data' para OAuth2
        login_data = {'username': email, 'password': password}
        success, token_data, status_code = api_request("post", "api/v1/users/token", data=login_data)

        if success:
            session['token'] = token_data.get('access_token')
            flash("Has iniciado sesión correctamente.", "success")
            
            next_page = request.args.get('next')
            if next_page and is_safe_url(next_page):
                return redirect(next_page)
            return redirect(url_for('index'))
        else:
            error_msg = token_data.get('detail', 'Correo o contraseña incorrectos.')
            flash(error_msg, "danger")
            return redirect(url_for('login'))

    return render_template('login.html', title="Iniciar Sesión")

@app.route('/register', methods=['GET', 'POST'])
def register():
    """Ruta para registrar un nuevo usuario."""
    if request.method == 'POST':
        user_data = {
            "username": request.form.get('username'),
            "email": request.form.get('email'),
            "password": request.form.get('password')
        }
        success, data, status_code = api_request("post", "api/v1/users/register", json=user_data)

        if success:
            flash("¡Cuenta creada con éxito! Por favor, inicia sesión.", "success")
            return redirect(url_for('login'))
        else:
            flash(f"Error al registrar el usuario: {data.get('detail')}", "danger")
            return redirect(url_for('register'))

    return render_template('register.html', title="Registrarse")

@app.route('/logout')
def logout():
    """Ruta para cerrar sesión."""
    session.clear()
    flash("Has cerrado la sesión.", "info")
    return redirect(url_for('index'))

# --- Rutas para Eventos ---

@app.route("/events")
def list_events():
    """Muestra una lista de todos los eventos."""
    events = []
    success, data, _ = api_request("get", "api/v1/events/")
    if success:
        events = data
    else:
        flash(f"No se pudieron cargar los eventos: {data.get('detail')}", "danger")
    
    return render_template("events_list.html", title="Eventos", events=events)

@app.route("/event/<int:event_id>")
def event_detail(event_id):
    """Muestra los detalles de un evento específico."""
    success, event, status_code = api_request("get", f"api/v1/events/{event_id}")
    if not success:
        flash(f"No se pudo cargar el evento: {event.get('detail')}", "danger")
        return redirect(url_for('list_events'))
        
    return render_template("event_detail.html", title=event.get('title', 'Detalle del Evento'), event=event)

# --- Manejadores de Errores Globales ---

@app.errorhandler(404)
def page_not_found(e):
    """Renderiza una página 404 personalizada."""
    return render_template('error.html', message="Página no encontrada.", title="Error 404"), 404

@app.errorhandler(500)
def internal_server_error(e):
    """Renderiza una página 500 personalizada."""
    return render_template('error.html', message="Ha ocurrido un error interno en el servidor.", title="Error 500"), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
