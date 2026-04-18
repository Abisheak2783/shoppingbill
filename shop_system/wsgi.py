"""
WSGI config for shop_system project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/6.0/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shop_system.settings')

# Guaranteed production initialization
try:
    from scripts.init_prod import init_production
    init_production()
except Exception as e:
    print(f"FAILED to run initialization: {e}")

application = get_wsgi_application()
