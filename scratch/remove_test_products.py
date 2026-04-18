import os
import django
import sys

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shop_system.settings')
django.setup()

from billing_app.models import Product

def remove_test_products():
    # Names from the screenshot
    target_names = ["Test Product Form", "Test Product with Image"]
    
    # Also targeting the exact SKUs/IDs if possible, but names are clear
    products = Product.objects.filter(name__in=target_names)
    count = products.count()
    
    for product in products:
        print(f"Deleting: {product.name} (SKU-{product.pk:04d})")
        product.delete()
        
    print(f"Successfully deleted {count} products.")

if __name__ == '__main__':
    remove_test_products()
