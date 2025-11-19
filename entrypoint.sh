#!/bin/bash

set -e

echo "Esperando a que PostgreSQL este listo..."

while ! nc -z db 5432; do
  sleep 1
done

echo "PostgreSQL conectado!"

echo "Aplicando migraciones de base de datos..."
python manage.py migrate

echo "Recopilando archivos estaticos..."
python manage.py collectstatic --noinput

echo "Iniciando servidor Django..."
python manage.py runserver 0.0.0.0:8000