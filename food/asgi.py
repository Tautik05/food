# """
# ASGI config for food project.

# It exposes the ASGI callable as a module-level variable named ``application``.

# For more information on this file, see
# https://docs.djangoproject.com/en/5.0/howto/deployment/asgi/
# """

# import os

# from django.core.asgi import get_asgi_application

# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'food.settings')

# application = get_asgi_application()


"""
ASGI config for food project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/howto/deployment/asgi/
"""

import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from home.routing import websocket_urlpatterns  # Import your websocket URL patterns

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'food.settings')

# Create your ASGI application
application = ProtocolTypeRouter({
    "http": get_asgi_application(),  # Handle HTTP requests
    "websocket": AuthMiddlewareStack(  # Handle WebSocket connections
        URLRouter(websocket_urlpatterns)  # Use your websocket URL patterns here
    ),
})
