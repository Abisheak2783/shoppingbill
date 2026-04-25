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
    try:
        django.setup()
    except Exception as e:
        print(f"Django setup error: {e}")
        return
    
    # 1. Run Migrations & Collectstatic
    print("Running database migrations...")
    call_command('migrate', interactive=False, database='default')
    
    print("Running runtime collectstatic (Guarantee phase)...")
    call_command('collectstatic', interactive=False, clear=True)
    
    # 2. RUN DIRECT DATA SYNC (Manual ORM injection)
    try:
        from scripts.sync_data import sync_all_data
        print("Starting Direct-Inject Data Synchronization...")
        sync_all_data()
    except Exception as e:
        print(f"FAILED to run data sync: {e}")

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

    # 4. Reset Sequences (Postgres only)
    from django.db import connection
    if connection.vendor == 'postgresql':
        print("Resetting database sequences (Postgres)...")
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
            """)
            tables = [row[0] for row in cursor.fetchall()]
            for table in tables:
                cursor.execute(f"""
                    SELECT a.attname
                    FROM   pg_index i
                    JOIN   pg_attribute a ON a.attrelid = i.indrelid AND a.attnum = ANY(i.indkey)
                    WHERE  i.indrelid = '{table}'::regclass AND i.indisprimary;
                """)
                pk_result = cursor.fetchone()
                if pk_result:
                    pk_col = pk_result[0]
                    try:
                        cursor.execute(f"SELECT setval(pg_get_serial_sequence('{table}', '{pk_col}'), coalesce(max({pk_col}), 1)) FROM {table};")
                    except: pass
        print("Sequences synchronized.")

if __name__ == '__main__':
    init_production()
