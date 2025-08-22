# dashboard/urls.py

from django.urls import path
from . import views

# This file needs to be created inside the 'dashboard' app directory.

app_name = 'dashboard'

urlpatterns = [
    # Main page
    path('', views.index, name='index'),

    # API endpoints for tools
    path('api/ping/', views.ping_host, name='ping_host'),
    path('api/dns-lookup/', views.dns_lookup, name='dns_lookup'),
    path('api/port-scan/', views.port_scan, name='port_scan'),
    path('api/ssl-check/', views.ssl_cert_check, name='ssl_cert_check'),
    path('api/ip-geo/', views.ip_geolocation, name='ip_geolocation'),
    path('api/connections/', views.get_network_connections, name='get_network_connections'),
]
