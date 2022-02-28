#!/bin/bash
set -e

cd /opt/emkn/
python manage.py showmigrations
python manage.py migrate
exec gunicorn choosing_electives.wsgi:application

#while true; do echo "test"; sleep 2; done

#cd /opt/emkn/
#exec gunicorn --access-logfile - --workers 4 --bind unix:/opt/emkn/electives.sock choosing_electives.wsgi:application
