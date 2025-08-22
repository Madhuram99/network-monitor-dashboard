#This sets up the ProtocolTypeRouter which acts as the initial traffic cop for incoming connections.

# network_monitor/asgi.py

import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
import dashboard.routing # We will create this file next

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'network_monitor.settings')

application = ProtocolTypeRouter({
    # Standard HTTP requests are handled by Django's ASGI app
    "http": get_asgi_application(),

    # WebSocket requests are handled by our custom routing
    "websocket": AuthMiddlewareStack(
        URLRouter(
            dashboard.routing.websocket_urlpatterns
        )
    ),
})
