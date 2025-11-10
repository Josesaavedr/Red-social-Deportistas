#!/bin/bash
set -e

# Asignar valores por defecto si las variables no están definidas
DB_HOST=${DB_HOST:-db}
DB_PORT=${DB_PORT:-5432}
DB_NAME=${DB_NAME:-deportistas_db}
DB_USER=${DB_USER:-deportistas_user}

# Verificar que las variables de entorno cruciales para Django estén presentes
if [ -z "$DB_NAME" ] || [ -z "$DB_USER" ] || [ -z "$DB_PASSWORD" ] || [ -z "$DB_HOST" ]; then
  echo "🚨 ERROR: Una o más variables de entorno de la base de datos (DB_NAME, DB_USER, DB_PASSWORD, DB_HOST) no están definidas."
  echo "Asegúrate de que el archivo .env existe y está configurado correctamente."
  exit 1
fi

echo "Esperando a que la base de datos en '$DB_HOST:$DB_PORT' esté lista..."

until pg_isready -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME"; do
  echo "⏳ Esperando base de datos..."
  sleep 2
done

echo "✅ Base de datos lista!"

echo "Ejecutando migraciones de la base de datos..."
# Un solo comando `migrate` es más seguro y gestiona todas las dependencias.
# Django aplicará las migraciones de todas las apps en el orden correcto.
python manage.py migrate --noinput

echo "Recopilando archivos estáticos..."
python manage.py collectstatic --noinput || true

echo "Iniciando servidor Django..."
exec "$@"
