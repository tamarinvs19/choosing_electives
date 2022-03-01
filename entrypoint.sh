#!/bin/bash
set -e

cd /opt/emkn/

python manage.py migrate --skip-checks
exec gunicorn choosing_electives.wsgi:application