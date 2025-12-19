#!/usr/bin/env bash
set -e

# Apply database migrations
echo "=> Running migrations..."
python manage.py migrate --noinput

# Collect static files
echo "=> Collecting static files..."
python manage.py collectstatic --noinput

# Start Gunicorn
echo "=> Starting gunicorn..."
exec gunicorn echo_project.wsgi:application \
  --bind 0.0.0.0:8000 \
  --workers 3 \
  --log-level info
