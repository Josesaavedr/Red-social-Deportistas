FROM python:3.11-slim

WORKDIR /app

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    postgresql-client \
    bash \
    netcat-openbsd \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el proyecto
COPY . .

# Hacer ejecutable el entrypoint
RUN chmod +x entrypoint.sh

# Exponer puerto
EXPOSE 8000

# Usar entrypoint para ejecutar migraciones antes de iniciar
ENTRYPOINT ["./entrypoint.sh"]
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]

