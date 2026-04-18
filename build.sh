# upgrade pip
python -m pip install --upgrade pip

# install dependencies
pip install --no-cache-dir -r requirements.txt

# clear old static files (prevents build errors on Render)
rm -rf staticfiles

# run build commands
python manage.py collectstatic --no-input
python manage.py migrate
