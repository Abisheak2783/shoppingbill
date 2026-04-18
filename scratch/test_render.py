import os
import django
from django.template import loader
from django.test import RequestFactory
from django.contrib.messages.storage.fallback import FallbackStorage

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shop_system.settings')
django.setup()

from billing_app.forms import ProductForm
from django.core.files.uploadedfile import SimpleUploadedFile

def test_render_error():
    try:
        # Simulate a failed POST request
        factory = RequestFactory()
        request = factory.post('/products/add/')
        
        # Add messages middleware support
        setattr(request, 'session', 'session')
        messages = FallbackStorage(request)
        setattr(request, '_messages', messages)
        
        # Create a form with an error (but we want to test the render after catch)
        data = {'name': 'Broken Product'}
        form = ProductForm(data=data)
        
        context = {'form': form, 'action': 'Add'}
        template = loader.get_template('product_form.html')
        rendered = template.render(context, request)
        print("Template rendered successfully!")
        
    except Exception as e:
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_render_error()
