# dashboard/routing.py

from django.urls import re_path
from . import consumers

# This file needs to be created inside the 'dashboard' app directory.

websocket_urlpatterns = [
    re_path(r'ws/network-monitor/$', consumers.NetworkMonitorConsumer.as_asgi()),
]
