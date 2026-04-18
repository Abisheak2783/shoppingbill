import os
import django
import sys
from django.core.management import call_command
from django.conf import settings

def init_production():
    # Force Absolute Project Root
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.append(project_root)
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shop_system.settings')
    django.setup()
    
    # Database Diagnostic
    db_config = settings.DATABASES.get('default', {})
    db_engine = db_config.get('ENGINE', 'Unknown')
    db_name = db_config.get('NAME', 'Unknown')
    print(f"DEBUG: Using Database Engine: {db_engine}")
    print(f"DEBUG: Using Database Name: {db_name}")
    
    # Check if we are on Postgres or SQLite
    if 'sqlite' in db_engine.lower():
        print("WARNING: THE SERVER IS USING SQLITE. Data might be lost on restart!")
    else:
        print("SUCCESS: THE SERVER IS USING POSTGRES. Data is persistent.")

    # 1. Run Migrations
    print("Running database migrations...")
    call_command('migrate', interactive=False, database='default')
    
    # 2. Aggressive Data Transfer File Search
    data_file = os.path.join(project_root, 'data_transfer.json')
    if os.path.exists(data_file):
        print(f"SUCCESS: Found data transfer file. Size: {os.path.getsize(data_file)} bytes.")
        try:
            # We explicitly target the 'default' database
            call_command('loaddata', data_file, verbosity=2, database='default')
            print("Data loaded successfully into 'default' database.")
        except Exception as e:
            print(f"ERROR: Failed to load data: {e}")
    else:
        print("CRITICAL: data_transfer.json NOT FOUND!")

    # 3. Ensure Superuser exists
    from django.contrib.auth import get_user_model
    User = get_user_model()
    username = 'admin'
    password = 'admin123'
    user, created = User.objects.get_or_create(username=username, defaults={'email': 'admin@example.com'})
    user.set_password(password)
    user.is_superuser = True
    user.is_staff = True
    user.save()
    print(f"User {username} is ready.")

if __name__ == '__main__':
    init_production()
