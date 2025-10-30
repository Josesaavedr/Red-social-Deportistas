# /frontend/app.py

from flask import Flask, render_template, request, redirect, url_for, session, flash
from datetime import datetime
import requests
import os
from common.config import settings # Importa la configuración global
from functools import wraps

app = Flask(__name__)
# Es crucial para usar sesiones de forma segura.
# En producción, esto debería ser una cadena larga y aleatoria.
app.secret_key = os.getenv("FLASK_SECRET_KEY", "super-secret-key-for-dev")

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

    """Ruta de la página de inicio."""

    page = request.args.get('page', 1, type=int)
    skip = (page - 1) * ACTIVITIES_PER_PAGE

    activities = []
    total_activities = 0

    try:
        # 1. Obtener el número total de actividades
        count_response = requests.get(f"{settings.API_GATEWAY_URL}/api/v1/activities/count")
        count_response.raise_for_status()
        total_activities = count_response.json().get('total', 0) # type: ignore

        # Obtener el token de la sesión para pasarlo al servicio de actividades
        headers = get_auth_headers() if 'token' in session else {}

        # 2. Obtener las actividades para la página actual
        if total_activities > 0:
            activities_response = requests.get(
                f"{settings.API_GATEWAY_URL}/api/v1/activities/?skip={skip}&limit={ACTIVITIES_PER_PAGE}"
            )
            activities_response = requests.get(f"{settings.API_GATEWAY_URL}/api/v1/activities/?skip={skip}&limit={ACTIVITIES_PER_PAGE}", headers=headers)
            activities = activities_response.json()

    except requests.exceptions.RequestException as e:
        print(f"Error al conectar con el API Gateway para obtener actividades: {e}")
        activities = []
        total_activities = 0

    total_pages = (total_activities + ACTIVITIES_PER_PAGE - 1) // ACTIVITIES_PER_PAGE

    # Pasa los datos a la plantilla para renderizarlos.
    return render_template("index.html", title="Inicio", activities=activities, page=page, total_pages=total_pages)

def login_required(f):
    """
    Decorador para proteger rutas que requieren autenticación.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'token' not in session:
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

def get_auth_headers():
    return {"Authorization": f"Bearer {session.get('token')}"}

@app.route("/new-item", methods=["GET", "POST"])
def new_item():
    """Ruta para crear un nuevo ítem."""
    if request.method == "POST":
        # Recoge los datos del formulario.
        title = request.form.get("title")
        content = request.form.get("content")

        # Validación básica de los datos del formulario
        if not title or not content:
            return "Error: Título y Detalles son requeridos.", 400

        activity_data = {
            "title": title,
            "content": content
        }
        
        # Envía los datos al API Gateway para crear una nueva actividad.
        try:
            response = requests.post(f"{settings.API_GATEWAY_URL}/api/v1/activities/", json=activity_data, headers=get_auth_headers())
            response.raise_for_status() # Lanza un error para códigos de estado 4xx/5xx
            flash("¡Actividad registrada con éxito!", "success")
            return redirect(url_for("index")) # TODO: Debería redirigir a la página de detalles de la nueva actividad
        except requests.exceptions.RequestException as e:
            print(f"Error al registrar la actividad: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"Respuesta del API Gateway: {e.response.text}")
            flash("Error al registrar la actividad. Por favor, inténtalo de nuevo más tarde.", "danger")
            return redirect(url_for('new_item'))

    return render_template("form.html", title="Registrar Nueva Actividad")

@app.route("/delete-activity/<int:activity_id>", methods=["POST"])
@login_required
def delete_activity(activity_id):
    """Ruta para eliminar una actividad."""
    try:
        # Envía la petición DELETE al API Gateway
        response = requests.delete(f"{settings.API_GATEWAY_URL}/api/v1/activities/{activity_id}", headers=get_auth_headers())
        response.raise_for_status() # Lanza un error para códigos de estado 4xx/5xx
        flash("Actividad eliminada correctamente.", "success")
        # Redirige a la página de inicio después de eliminar
        return redirect(url_for("index"))
    except requests.exceptions.RequestException as e:
        print(f"Error al eliminar la actividad: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Respuesta del API Gateway: {e.response.text}")
        flash("Error al eliminar la actividad. Solo el autor puede eliminarla.", "danger")
        return redirect(request.referrer or url_for('index'))

@app.route("/activity/<int:activity_id>")
def activity_detail(activity_id):
    """Ruta para ver los detalles de una actividad específica."""
    activity, comments = None, []
    try:
        # 1. Obtener los detalles de la actividad
        headers = get_auth_headers() if 'token' in session else {}
        response = requests.get(f"{settings.API_GATEWAY_URL}/api/v1/activities/{activity_id}", headers=headers)
        response.raise_for_status()
        activity = response.json()

        # 2. Obtener los comentarios de la actividad
        comments_response = requests.get(f"{settings.API_GATEWAY_URL}/api/v1/activities/{activity_id}/comments")
        comments_response.raise_for_status()
        comments = comments_response.json()

    except requests.exceptions.RequestException as e:
        print(f"Error al obtener los detalles de la actividad: {e}")
        # Puedes manejar el error mostrando una página de error específica
        return "Error al cargar la actividad o la actividad no existe.", 404

    if not activity:
        return "Actividad no encontrada.", 404

    return render_template("activity_detail.html", title=activity.get('title', 'Detalle de Actividad'), activity=activity, comments=comments)

@app.route("/activity/<int:activity_id>/comment", methods=["POST"])
@login_required
def add_comment(activity_id):
    """Ruta para añadir un nuevo comentario a una actividad."""
    content = request.form.get("content")
    if not content:
        return "Error: El contenido del comentario es requerido.", 400

    try:
        response = requests.post(f"{settings.API_GATEWAY_URL}/api/v1/activities/{activity_id}/comments", json={"content": content}, headers=get_auth_headers())
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Error al añadir el comentario: {e}")
        flash("Error al publicar el comentario.", "danger")

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

        try:
            # Envía la petición PUT al API Gateway
            response = requests.put(f"{settings.API_GATEWAY_URL}/api/v1/activities/{activity_id}", json=updated_data, headers=get_auth_headers())
            response.raise_for_status()
            flash("Actividad actualizada correctamente.", "success")
            # Redirige a la página de detalles después de editar
            return redirect(url_for('activity_detail', activity_id=activity_id))
        except requests.exceptions.RequestException as e:
            print(f"Error al actualizar la actividad: {e}")
            flash("Error al actualizar la actividad. Solo el autor puede editarla.", "danger")
            return redirect(url_for('edit_activity', activity_id=activity_id))

    # Método GET: Muestra el formulario de edición
    activity = None
    try:
        # Llama al API Gateway para obtener los datos actuales de la actividad
        response = requests.get(f"{settings.API_GATEWAY_URL}/api/v1/activities/{activity_id}")
        response.raise_for_status()
        activity = response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error al obtener la actividad para editar: {e}")
        return "Error al cargar la actividad para editar.", 404

    if not activity:
        return "Actividad no encontrada.", 404

    return render_template("edit_activity.html", activity=activity)

@app.route("/like-activity/<int:activity_id>", methods=["POST"]) # Cambiado a POST para enviar user_id
@login_required
def like_activity(activity_id):
    """Ruta para dar 'Me gusta' a una actividad."""
    try:
        response = requests.post(f"{settings.API_GATEWAY_URL}/api/v1/activities/{activity_id}/like", headers=get_auth_headers())
        if response.status_code == 409: # Conflicto, ya le dio "Me gusta"
            flash("Ya has indicado que te gusta esta actividad.", "info")
        else:
            response.raise_for_status()
            flash("¡Gracias por tu 'Me gusta'!", "success")
    except requests.exceptions.RequestException as e:
        print(f"Error al dar 'Me gusta' a la actividad: {e}")
        flash("No se pudo registrar tu 'Me gusta'.", "danger")
    
    # Redirige al usuario a la página desde la que vino
    return redirect(request.referrer or url_for('index'))

@app.route("/unlike-activity/<int:activity_id>", methods=["POST"])
@login_required
def unlike_activity(activity_id):
    """Ruta para quitar 'Me gusta' a una actividad."""
    try:
        # Llama al endpoint DELETE del API Gateway
        response = requests.delete(f"{settings.API_GATEWAY_URL}/api/v1/activities/{activity_id}/like", headers=get_auth_headers())
        if response.status_code == 404: # No se encontró el "like" para eliminar
            flash("No habías indicado que te gusta esta actividad.", "info")
        else:
            response.raise_for_status()
            flash("Has quitado tu 'Me gusta'.", "success")
    except requests.exceptions.RequestException as e:
        print(f"Error al quitar 'Me gusta' a la actividad: {e}")
        flash("No se pudo quitar tu 'Me gusta'.", "danger")
    
    return redirect(request.referrer or url_for('index'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Ruta para iniciar sesión."""
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        try:
            # El servicio de usuarios espera los datos en formato 'form-data' para OAuth2
            login_data = {'username': email, 'password': password}
            # Asumiendo que el gateway expone el endpoint de token del servicio de usuarios
            response = requests.post(f"{settings.API_GATEWAY_URL}/api/v1/users/token", data=login_data)
            response.raise_for_status()
            
            token_data = response.json()
            session['token'] = token_data.get('access_token')
            
            # Opcional: decodificar el token para obtener el user_id y guardarlo
            # from jose import jwt
            # payload = jwt.decode(session['token'], os.getenv("JWT_SECRET"), algorithms=["HS256"])
            # session['user_id'] = payload.get('sub')

            flash("Has iniciado sesión correctamente.", "success")
            return redirect(url_for('index'))
        except requests.exceptions.RequestException as e:
            print(f"Error en el inicio de sesión: {e}")
            flash("Correo o contraseña incorrectos.", "danger")
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
        try:
            # Asumiendo que el gateway expone el endpoint de registro del servicio de usuarios
            response = requests.post(f"{settings.API_GATEWAY_URL}/api/v1/users/register", json=user_data)
            response.raise_for_status()
            flash("¡Cuenta creada con éxito! Por favor, inicia sesión.", "success")
            # Redirigir a la página de login después de un registro exitoso
            return redirect(url_for('login'))
        except requests.exceptions.RequestException as e:
            print(f"Error en el registro: {e}")
            flash("Error al registrar el usuario. El correo puede que ya esté en uso.", "danger")
            return redirect(url_for('register'))

    return render_template('register.html', title="Registrarse")

@app.route('/logout')
def logout():
    """Ruta para cerrar sesión."""
    session.clear()
    flash("Has cerrado la sesión.", "info")
    return redirect(url_for('index'))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
