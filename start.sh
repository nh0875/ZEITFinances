#!/bin/sh
set -e
python manage.py migrate
exec gunicorn finanzas.wsgi:application
