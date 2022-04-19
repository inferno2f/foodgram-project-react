FROM python:3.9.12-slim

RUN apt update && apt install -y gcc libpq-dev

WORKDIR /app

COPY ./ /app

RUN pip3 install -r /app/backend/requirements.txt --no-cache-dir && \
    chmod +x /app/docker-entrypoint.sh
