#!/bin/sh
cd backend/
python manage.py migrate
python manage.py runscript load
python manage.py collectstatic --noinput
gunicorn --bind 0:8000 foodgram.wsgi
