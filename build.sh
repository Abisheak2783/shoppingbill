# install dependencies
pip install -r requirements.txt

# clear old static files (prevents build errors on Render)
rm -rf staticfiles

# run build commands
python manage.py collectstatic --no-input
python manage.py migrate
