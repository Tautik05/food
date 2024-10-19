# routing.py

from django.urls import path
from . import consumers  # Import your consumer

websocket_urlpatterns = [
    path('ws/order/', consumers.OrderConsumer.as_asgi()),  # Change the path as needed
]
