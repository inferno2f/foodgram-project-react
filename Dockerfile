FROM python:3.9.12-slim

RUN apt update && apt install -y gcc libpq-dev

WORKDIR /app/backend

COPY ./ /app

RUN pip3 install -r /app/backend/requirements.txt --no-cache-dir

CMD ["gunicorn", "foodgram.wsgi:application", "--bind", "0:8000"]
