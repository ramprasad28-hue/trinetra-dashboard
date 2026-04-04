"""
ASGI config for trinetra project.
"""
import os
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'trinetra.settings')
application = get_asgi_application()
