import sys
import os
import django

# Add the project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shop_system.settings')
django.setup()

from billing_app.models import Product
from django.core.files import File

def reupload():
    products = Product.objects.all()
    media_root = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'media')
    for p in products:
        if p.image:
            # Get the base filename
            filename = os.path.basename(p.image.name)
            local_path = os.path.join(media_root, 'product_images', filename)
            
            if os.path.exists(local_path):
                print(f"Uploading {filename} for {p.name}...")
                with open(local_path, 'rb') as f:
                    p.image.save(f'product_images/{filename}', File(f), save=True)
                print(f"SUCCESS: {p.image.url}")
            else:
                print(f"Local file not found: {local_path}")

if __name__ == "__main__":
    reupload()
