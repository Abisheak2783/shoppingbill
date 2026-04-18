import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shop_system.settings')
django.setup()

from billing_app.forms import ProductForm
from django.core.files.uploadedfile import SimpleUploadedFile

def test_form_upload():
    try:
        # Create a dummy image
        image_content = b'GIF89a\x01\x00\x01\x00\x80\x00\x00\x00\x00\x00\xff\xff\xff!\xf9\x04\x01\x00\x00\x00\x00,\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02D\x01\x00;'
        image_file = SimpleUploadedFile('test_form.gif', image_content, content_type='image/gif')
        
        data = {
            'name': 'Test Product Form',
            'price': '15.50',
            'stock_quantity': '5',
            'low_stock_threshold': '2',
        }
        files = {
            'image': image_file
        }
        
        form = ProductForm(data=data, files=files)
        if form.is_valid():
            product = form.save()
            print(f"Product created via form: {product.id}")
            print(f"Image URL: {product.image.url}")
        else:
            print("Form invalid:")
            print(form.errors)
            
    except Exception as e:
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_form_upload()
