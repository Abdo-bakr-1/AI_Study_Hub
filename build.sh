#!/usr/bin/env bash
# Render build step: prepare static files and database before the app starts.
set -o errexit

python manage.py collectstatic --noinput
python manage.py migrate --noinput
