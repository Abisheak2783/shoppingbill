import json
import os
import django
import sys

def sync_all_data():
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.append(project_root)
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shop_system.settings')
    try:
        django.setup()
    except Exception as e:
        print(f"Django setup error: {e}")
        return

    from billing_app.models import Category, Product, Bill, BillItem
    from django.contrib.auth import get_user_model
    User = get_user_model()

    data_file = os.path.join(project_root, 'data_transfer.json')
    if not os.path.exists(data_file):
        print(f"Data file not found at {data_file}")
        return

    with open(data_file, 'r') as f:
        data = json.load(f)

    print(f"Syncing {len(data)} objects...")

    # Load categories first
    categories_data = [obj for obj in data if obj['model'] == 'billing_app.category']
    for entry in categories_data:
        fields = entry['fields']
        obj, created = Category.objects.get_or_create(
            id=entry['pk'],
            defaults={'name': fields['name'], 'description': fields['description']}
        )
        if created: print(f"Created Category: {fields['name']}")

    # Load products (requires category)
    products_data = [obj for obj in data if obj['model'] == 'billing_app.product']
    for entry in products_data:
        fields = entry['fields']
        try:
            category = Category.objects.get(id=fields['category'])
            obj, created = Product.objects.update_or_create(
                id=entry['pk'],
                defaults={
                    'name': fields['name'],
                    'category': category,
                    'image': fields['image'],
                    'price': fields['price'],
                    'stock_quantity': fields['stock_quantity'],
                    'low_stock_threshold': fields['low_stock_threshold'],
                    'created_at': fields['created_at']
                }
            )
            if created: print(f"Created Product: {fields['name']}")
        except Category.DoesNotExist:
            print(f"Skipping product {fields['name']} - Category {fields['category']} missing")

    # Load Bills (requires user)
    admin_user = User.objects.filter(is_superuser=True).first()
    bills_data = [obj for obj in data if obj['model'] == 'billing_app.bill']
    for entry in bills_data:
        fields = entry['fields']
        obj, created = Bill.objects.update_or_create(
            id=entry['pk'],
            defaults={
                'admin_user': admin_user,
                'customer_name': fields['customer_name'],
                'customer_phone': fields['customer_phone'],
                'total_amount': fields['total_amount'],
                'discount': fields['discount'],
                'gst_amount': fields['gst_amount'],
                'final_amount': fields['final_amount'],
                'created_at': fields['created_at']
            }
        )
        if created: print(f"Synced Bill: {entry['pk']}")

    # Load Bill Items (requires bill and product)
    items_data = [obj for obj in data if obj['model'] == 'billing_app.billitem']
    for entry in items_data:
        fields = entry['fields']
        try:
            bill = Bill.objects.get(id=fields['bill'])
            product = Product.objects.get(id=fields['product'])
            obj, created = BillItem.objects.update_or_create(
                id=entry['pk'],
                defaults={
                    'bill': bill,
                    'product': product,
                    'quantity': fields['quantity'],
                    'price': fields['price'],
                    'total': fields['total']
                }
            )
        except (Bill.DoesNotExist, Product.DoesNotExist):
            pass

    print(f"Data Sync Complete. Total Products: {Product.objects.count()}")

if __name__ == '__main__':
    sync_all_data()
