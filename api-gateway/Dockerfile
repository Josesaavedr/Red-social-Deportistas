FROM python:3.11-slim

# Establece variables de entorno para optimizar la ejecución de Python en Docker.
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Establece el directorio de trabajo en el contenedor.
WORKDIR /app

# Copia el archivo de requerimientos primero para aprovechar el cache de Docker.
COPY requirements.txt .

# Crea un usuario no-root para ejecutar la aplicación de forma segura.
RUN addgroup --system nonroot && adduser --system --ingroup nonroot nonroot

# Instala las dependencias.
RUN pip install --no-cache-dir -r requirements.txt

# Copia el resto de los archivos de la aplicación y establece la propiedad.
COPY --chown=nonroot:nonroot main.py .

# Cambia al usuario no-root.
USER nonroot

# Expone el puerto en el que se ejecutará la aplicación.
EXPOSE 8000

# Define el comando para ejecutar la aplicación con Uvicorn.
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]