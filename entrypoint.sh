#!/bin/bash
set -e

cd /opt/emkn/

python manage.py migrate --skip-checks
python manage.py createsuperuser --email test@test.com --username superuser --noinput

exec gunicorn --bind 0.0.0.0:${PORT:-8000} choosing_electives.wsgi:application
