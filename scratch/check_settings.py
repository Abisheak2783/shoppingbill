import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shop_system.settings')
django.setup()

from django.conf import settings

def check_config():
    print(f"DEBUG: {settings.DEBUG}")
    print(f"CLOUDINARY_STORAGE: {settings.CLOUDINARY_STORAGE}")
    
    # Check if is_cloudinary_configured would be true
    cloud_name = settings.CLOUDINARY_STORAGE.get('CLOUD_NAME')
    is_configured = cloud_name and cloud_name != 'your_cloud_name'
    print(f"Is Cloudinary configured? {is_configured}")
    
    print(f"Default storage backend: {settings.STORAGES['default']['BACKEND']}")

if __name__ == '__main__':
    check_config()
