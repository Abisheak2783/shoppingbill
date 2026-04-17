import os
import sys
import django

sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shop_system.settings')
django.setup()

from billing_app.models import Category

categories = ["rice", "idly rice", "cow feed"]

for cat_name in categories:
    obj, created = Category.objects.get_or_create(name=cat_name)
    if created:
        print(f"Created category: {cat_name}")
    else:
        print(f"Category already exists: {cat_name}")
