import os
import django
import sys
from django.core.management import call_command

def init_production():
    # Add project root to path
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shop_system.settings')
    django.setup()
    
    # 1. Run Migrations & Collectstatic
    print("Running database migrations...")
    call_command('migrate', interactive=False)
    
    print("Running runtime collectstatic (Guarantee phase)...")
    call_command('collectstatic', interactive=False, clear=True)
    
    # 2. Check for Data Transfer file and Load it
    data_file = os.path.join(os.environ.get('BASE_DIR', os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'data_transfer.json')
    if os.path.exists(data_file):
        print(f"FOUND data transfer file: {data_file}. Loading data...")
        try:
            call_command('loaddata', data_file)
            print("Data loaded successfully.")
        except Exception as e:
            print(f"ERROR loading data: {e}")
    else:
        print("No data transfer file found. Skipping data import.")
    
    # 2. Ensure Superuser exists and has correct password
    from django.contrib.auth import get_user_model
    User = get_user_model()
    
    username = os.environ.get('DJANGO_SUPERUSER_USERNAME', 'admin')
    email = os.environ.get('DJANGO_SUPERUSER_EMAIL', 'admin@example.com')
    password = os.environ.get('DJANGO_SUPERUSER_PASSWORD', 'admin123')
    
    user, created = User.objects.get_or_create(username=username, defaults={'email': email})
    
    if created:
        print(f"Created new superuser: {username}")
    else:
        print(f"Updating existing superuser: {username}")
    
    user.set_password(password)
    user.is_superuser = True
    user.is_staff = True
    user.save()
    print(f"Password for {username} is GUARANTEED to be 'admin123'.")
    
    # 3. Diagnostic: Check and Log static files existence
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    static_root = os.path.join(project_root, 'staticfiles')
    css_dir = os.path.join(static_root, 'css')
    
    print(f"Diagnostic: Project root: {project_root}")
    print(f"Diagnostic: Static root: {static_root}")
    
    if os.path.exists(static_root):
        file_count = sum([len(files) for r, d, files in os.walk(static_root)])
        print(f"Diagnostic: SUCCESS - {file_count} static files found in staticfiles directory.")
        
        if os.path.exists(css_dir):
            css_files = os.listdir(css_dir)
            print(f"Diagnostic: CSS folder contents: {css_files}")
    else:
        print("Diagnostic: ERROR - staticfiles directory NOT FOUND!")

if __name__ == '__main__':
    init_production()
