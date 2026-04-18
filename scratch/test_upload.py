import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shop_system.settings')
django.setup()

from billing_app.models import Product, Category
from django.core.files.uploadedfile import SimpleUploadedFile

def test_add_product():
    try:
        # Create a dummy image
        image_content = b'GIF89a\x01\x00\x01\x00\x80\x00\x00\x00\x00\x00\xff\xff\xff!\xf9\x04\x01\x00\x00\x00\x00,\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02D\x01\x00;'
        image = SimpleUploadedFile('test.gif', image_content, content_type='image/gif')
        
        product = Product.objects.create(
            name='Test Product with Image',
            price=10.00,
            stock_quantity=10,
            image=image
        )
        print(f"Product created successfully: {product.id}")
        print(f"Image URL: {product.image.url}")
        
    except Exception as e:
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_add_product()
