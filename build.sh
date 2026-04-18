#!/usr/bin/env bash
# exit on error
set -o errexit

# upgrade pip
python -m pip install --upgrade pip

# install dependencies
pip install --no-cache-dir -r requirements.txt

# clear old static files (prevents build errors on Render)
rm -rf staticfiles

# run build commands
# Only static files here. No database migrations!
python manage.py collectstatic --no-input
