import os
import django
import sys
from django.core.management import call_command

def init_production():
    # Force Absolute Project Root
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.append(project_root)
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shop_system.settings')
    django.setup()
    
    print(f"DEBUG: Current Working Directory: {os.getcwd()}")
    print(f"DEBUG: Project Root: {project_root}")
    
    # 1. Run Migrations & Collectstatic
    print("Running database migrations...")
    call_command('migrate', interactive=False)
    
    print("Running runtime collectstatic (Guarantee phase)...")
    call_command('collectstatic', interactive=False, clear=True)
    
    # 2. Aggressive Data Transfer File Search
    # We look in the root folder for data_transfer.json
    data_file = os.path.join(project_root, 'data_transfer.json')
    
    print(f"Checking for data file at: {data_file}")
    
    if os.path.exists(data_file):
        print(f"SUCCESS: Found data transfer file. Size: {os.path.getsize(data_file)} bytes.")
        print("Loading data into production database...")
        try:
            # We use verbosity=2 to see what is happening in the logs
            call_command('loaddata', data_file, verbosity=2)
            print("Data loaded successfully.")
        except Exception as e:
            print(f"ERROR: Failed to load data: {e}")
    else:
        print("WARNING: data_transfer.json NOT FOUND in root. Searching recursively...")
        found = False
        for root, dirs, files in os.walk(project_root):
            if 'data_transfer.json' in files:
                found_path = os.path.join(root, 'data_transfer.json')
                print(f"FOUND recursively at: {found_path}")
                try:
                    call_command('loaddata', found_path, verbosity=2)
                    print("Data loaded successfully from recursive path.")
                    found = True
                    break
                except Exception as e:
                    print(f"ERROR: Failed to load from recursive path: {e}")
        if not found:
            print("CRITICAL: data_transfer.json is missing from the entire project!")

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
