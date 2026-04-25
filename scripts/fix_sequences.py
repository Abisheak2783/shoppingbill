import os
import django
import sys

# Add the project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shop_system.settings')
django.setup()

from django.db import connection

def reset_sequences():
    print("Resetting database sequences to fix duplicate key errors...")
    with connection.cursor() as cursor:
        # Get all tables in the public schema
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
        """)
        tables = [row[0] for row in cursor.fetchall()]
        
        for table in tables:
            # For each table, find the primary key column (usually 'id')
            cursor.execute(f"""
                SELECT a.attname
                FROM   pg_index i
                JOIN   pg_attribute a ON a.attrelid = i.indrelid
                                     AND a.attnum = ANY(i.indkey)
                WHERE  i.indrelid = '{table}'::regclass
                AND    i.indisprimary;
            """)
            pk_result = cursor.fetchone()
            if pk_result:
                pk_col = pk_result[0]
                try:
                    # Reset the sequence for this table
                    sql = f"SELECT setval(pg_get_serial_sequence('{table}', '{pk_col}'), coalesce(max({pk_col}), 1)) FROM {table};"
                    cursor.execute(sql)
                    print(f"  - Reset sequence for {table} ({pk_col})")
                except Exception as e:
                    # Some tables might not have sequences or might cause errors
                    pass

    print("Successfully synchronized all database sequences.")

if __name__ == "__main__":
    reset_sequences()
