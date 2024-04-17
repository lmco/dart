#!/bin/bash
set -e

echo "migrations"
python manage.py makemigrations --noinput
python manage.py migrate
echo "migrations DONE!"

exec "$@"