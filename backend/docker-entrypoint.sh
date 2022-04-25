#!/bin/sh
python manage.py migrate
python manage.py runscript load
python manage.py collectstatic --noinput
gunicorn foodgram.wsgi:application --bind 0:8000
