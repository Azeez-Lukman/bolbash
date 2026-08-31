#!/usr/bin/env bash
# exit on error
set -o errexit

# Upgrade pip and install production dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Collect static files with Whitenoise compression
python manage.py collectstatic --no-input

# Run database migrations
python manage.py migrate --no-input
