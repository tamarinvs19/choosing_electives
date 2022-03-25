#!/bin/bash

fail_deploy() {
    if [ -n "$1" ]; then
        echo "Failing deployment: $1"
    else
        echo "Failing deployment"
    fi
    exit 1  # proceed no further!
}

#set -e

cd /opt/emkn/


python manage.py migrate --skip-checks

SUPERUSER_EXISTS_MSG="CommandError: Error: That username is already taken."
SUPERUSER_OUTPUT=$(python manage.py createsuperuser --email test@test.com --username superuser --noinput 2>&1)
SUPERUSER_STATUS=$?

echo "createsuperuser result: $SUPERUSER_STATUS - output: $SUPERUSER_OUTPUT"


if [ $SUPERUSER_STATUS -ne 0 ]; then
    # Manage.py createsuperuser did not finish with success:

    if [ "$SUPERUSER_OUTPUT" = "$SUPERUSER_EXISTS_MSG" ]; then
      # The message it printed in stderr was SUPERUSER_EXISTS_MSG.
      # This means the superuser already exists, so we continue.
      echo "Superuser already exists"
    else
      # The message in stderr was not SUPERUSER_EXISTS_MSG, so we stop.
      echo "Unknown error"
      fail_deploy "Create Superuser Failed"
    fi
fi

exec gunicorn --bind 0.0.0.0:${PORT:-8000} choosing_electives.wsgi:application
