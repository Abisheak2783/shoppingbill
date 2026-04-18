import os
import django
import sys
from django.core.management import call_command

def init_production():
    # Add project root to path
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shop_system.settings')
    django.setup()
    
    # 1. Run Migrations
    print("Running database migrations...")
    call_command('migrate', interactive=False)
    
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
    print(f"Password for {username} has been set/reset successfully.")
    
    # 3. Diagnostic: Check static files
    static_root = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'staticfiles')
    if os.path.exists(static_root):
        file_count = sum([len(files) for r, d, files in os.walk(static_root)])
        print(f"Diagnostic: {file_count} static files found in staticfiles directory.")
    else:
        print("Diagnostic: staticfiles directory NOT FOUND!")

if __name__ == '__main__':
    init_production()
