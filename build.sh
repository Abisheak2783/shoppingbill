#!/usr/bin/env bash
# exit on error
set -o errexit
# trace commands
set -x

# upgrade pip
python -m pip install --upgrade pip

# install dependencies
pip install --no-cache-dir -r requirements.txt

# Diagnostic: List files to ensure 'static' is where we think it is
ls -R static

# run build commands
# Use --clear to ensure no stale files interfere
python manage.py collectstatic --no-input --clear
