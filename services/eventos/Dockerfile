FROM python:3.12-slim

# Establece variables de entorno para optimizar la ejecución de Python en Docker.
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

COPY requirements.txt .

# Crea un usuario no-root para ejecutar la aplicación de forma segura.
RUN addgroup --system nonroot && adduser --system --ingroup nonroot nonroot

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Cambia la propiedad de los archivos al usuario no-root.
RUN chown -R nonroot:nonroot /app

# Cambia al usuario no-root.
USER nonroot

# Define el comando para ejecutar la aplicación con Uvicorn.
# El servicio escuchará en el puerto 8000 dentro del contenedor.
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
