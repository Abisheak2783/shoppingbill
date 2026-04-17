import os
import django
from django.urls import resolve, reverse

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shop_system.settings')
django.setup()

try:
    print(f"Reversing 'dashboard': {reverse('dashboard')}")
    match = resolve('/')
    print(f"Resolving '/': {match.func} (name: {match.url_name})")
except Exception as e:
    print(f"Error: {e}")
