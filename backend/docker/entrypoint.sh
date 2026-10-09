#!/bin/sh
set -eu

echo "Waiting for PostgreSQL..."
until python -c "import os, psycopg2; psycopg2.connect(host=os.environ['DB_HOST'], port=os.environ.get('DB_PORT', '5432'), dbname=os.environ['DB_NAME'], user=os.environ['DB_USER'], password=os.environ['DB_PASSWORD'])" 2>/dev/null; do
  sleep 2
done

python manage.py migrate --noinput
python manage.py collectstatic --noinput

exec python manage.py runserver 0.0.0.0:8000
