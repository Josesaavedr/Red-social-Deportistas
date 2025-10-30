FROM python:3.12-slim

# Establece el directorio de trabajo dentro del contenedor.
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

# Copia el archivo de dependencias.
COPY requirements.txt .

# Crea un usuario no-root para ejecutar la aplicación
RUN addgroup --system nonroot && adduser --system --ingroup nonroot nonroot

# Instala las dependencias. Usamos una rueda virtual para una instalación más limpia.
RUN pip install --no-cache-dir -r requirements.txt

# Copia el resto de los archivos de la aplicación (código, templates, estáticos).
COPY . .

# Cambia la propiedad de los archivos al usuario no-root
RUN chown -R nonroot:nonroot /app

# Cambia al usuario no-root
USER nonroot

# Exponemos el puerto en el que la aplicación Flask se ejecutará.
EXPOSE 5000

# Ejecuta la aplicación usando Gunicorn. Asume que tu instancia de Flask se llama 'app' en 'app.py'.
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]
