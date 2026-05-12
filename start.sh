#!/bin/sh
set -e

python3 manage.py migrate
python3 manage.py collectstatic --noinput
exec gunicorn telemaster74.wsgi:application --bind 0.0.0.0:80
