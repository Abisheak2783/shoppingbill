#!/usr/bin/env bash
# exit on error
set -o errexit

# upgrade pip
python -m pip install --upgrade pip

# install dependencies
pip install --no-cache-dir -r requirements.txt

# run build commands
# Only static files here. Standard storage to avoid crashes!
python manage.py collectstatic --no-input
