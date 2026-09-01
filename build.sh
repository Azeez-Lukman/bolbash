#!/usr/bin/env bash
# exit on error
set -o errexit

# Upgrade pip and install production dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Collect static files with Whitenoise compression
python manage.py collectstatic --no-input

# Run database migrations if database is available
python manage.py migrate --no-input || echo "[WARNING] Database migration failed or skipped. Please verify your cloud DATABASE_URL environment variable."

# Seed essential production data & sync media assets
python manage.py seed_production_content || echo "[WARNING] Production content seeding skipped or database not reachable."


