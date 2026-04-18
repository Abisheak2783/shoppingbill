#!/usr/bin/env bash
# exit on error
set -o errexit
# trace commands
set -x

# upgrade pip
python -m pip install --upgrade pip

# install dependencies
pip install --no-cache-dir -r requirements.txt

# run build commands
# Purely static files using Safe-Mode storage (Standard Django)
python manage.py collectstatic --no-input
