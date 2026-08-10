# Railway deployment image.
# Railway builds from this Dockerfile (it takes precedence over Nixpacks),
# injects DATABASE_URL at runtime, and runs the container start command.
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# Install dependencies first (better layer caching on rebuilds).
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the project.
COPY . .

# Collect static files at build time (does not need a database).
RUN python manage.py collectstatic --noinput

# Run migrations at startup (idempotent), then serve via gunicorn.
# PORT is injected by Railway.
CMD ["sh", "-c", "python manage.py migrate --noinput && gunicorn config.wsgi:application --bind 0.0.0.0:$PORT --workers 2 --timeout 120"]
