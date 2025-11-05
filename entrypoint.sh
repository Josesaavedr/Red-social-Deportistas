#!/bin/bash
set -e

echo "Esperando a que la base de datos esté lista..."
DB_HOST=${DB_HOST:-db}
DB_PORT=${DB_PORT:-5432}
DB_USER=${DB_USER:-deportistas_user}

until pg_isready -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER"; do
  echo "⏳ Esperando base de datos..."
  sleep 2
done

echo "✅ Base de datos lista!"

echo "Ejecutando migraciones..."
python manage.py makemigrations --noinput || true

# Aplicar migraciones base primero
echo "Aplicando migraciones base..."
python manage.py migrate contenttypes --noinput
python manage.py migrate auth --noinput
python manage.py migrate sessions --noinput
python manage.py migrate admin --noinput

# Aplicar migraciones de apps locales
echo "Aplicando migraciones de apps locales..."
python manage.py migrate usuarios --noinput
python manage.py migrate publicaciones --noinput
python manage.py migrate eventos --noinput
python manage.py migrate seguimientos --noinput

# Aplicar migraciones de terceros (authtoken necesita usuarios)
echo "Aplicando migraciones de terceros..."
python manage.py migrate --noinput

echo "Recopilando archivos estáticos..."
python manage.py collectstatic --noinput || true

echo "Iniciando servidor Django..."
exec "$@"

