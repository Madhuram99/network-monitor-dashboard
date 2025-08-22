# dashboard/views.py

import json
import socket
import ssl
import subprocess
import psutil
import requests
import platform  # Import the platform module
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_POST

# --- Main Page ---

def index(request):
    """
    Renders the main dashboard page.
    """
    return render(request, 'dashboard/index.html')

# --- Network Utilities API Endpoints ---

@require_POST
def ping_host(request):
    """
    Pings a host and returns the output.
    Uses subprocess to run the system's ping command, now with OS detection.
    """
    try:
        data = json.loads(request.body)
        host = data.get('host')
        if not host:
            return JsonResponse({'error': 'Host is required'}, status=400)

        # Determine the correct ping command based on the operating system
        system = platform.system().lower()
        if system == "windows":
            command = ['ping', '-n', '4', host]
        else:
            command = ['ping', '-c', '4', host]

        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=15 # Add a timeout to prevent hanging indefinitely
        )
        
        if result.returncode == 0:
            return JsonResponse({'output': result.stdout})
        else:
            return JsonResponse({'error': result.stderr or "Ping failed. Host may be unreachable or invalid."}, status=400)
    except subprocess.TimeoutExpired:
        return JsonResponse({'error': f'Ping timed out for host: {host}'}, status=408)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@require_POST
def dns_lookup(request):
    """
    Performs a DNS lookup for a given hostname.
    """
    try:
        data = json.loads(request.body)
        host = data.get('host')
        if not host:
            return JsonResponse({'error': 'Host is required'}, status=400)
        
        ip_address = socket.gethostbyname(host)
        return JsonResponse({'host': host, 'ip_address': ip_address})
    except socket.gaierror:
        return JsonResponse({'error': f"Could not resolve hostname: {host}"}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

# --- Security Tools API Endpoints ---

@require_POST
def port_scan(request):
    """
    Scans a range of ports on a target IP address.
    This is a simplified, slow, and blocking scanner.
    A real-world app should use Celery and a more robust scanning library.
    """
    try:
        data = json.loads(request.body)
        target = data.get('target')
        ports_str = data.get('ports', '22,80,443,3389,8080')
        
        if not target:
            return JsonResponse({'error': 'Target host is required'}, status=400)

        open_ports = []
        ports_to_scan = [int(p.strip()) for p in ports_str.split(',')]

        for port in ports_to_scan:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                socket.setdefaulttimeout(0.5) # Timeout for each connection attempt
                result = s.connect_ex((target, port))
                if result == 0:
                    open_ports.append(port)
        
        return JsonResponse({'target': target, 'open_ports': open_ports})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@require_POST
def ssl_cert_check(request):
    """
    Checks the SSL certificate for a given domain.
    """
    try:
        data = json.loads(request.body)
        domain = data.get('domain')
        if not domain:
            return JsonResponse({'error': 'Domain is required'}, status=400)

        context = ssl.create_default_context()
        with socket.create_connection((domain, 443)) as sock:
            with context.wrap_socket(sock, server_hostname=domain) as ssock:
                cert = ssock.getpeercert()
                
                # Format the certificate data for easy display
                cert_info = {
                    'subject': dict(x[0] for x in cert.get('subject', [])),
                    'issuer': dict(x[0] for x in cert.get('issuer', [])),
                    'version': cert.get('version'),
                    'serialNumber': cert.get('serialNumber'),
                    'notBefore': cert.get('notBefore'),
                    'notAfter': cert.get('notAfter'),
                    'subjectAltName': cert.get('subjectAltName')
                }
                return JsonResponse({'domain': domain, 'certificate': cert_info})
    except Exception as e:
        return JsonResponse({'error': f"Could not retrieve certificate for {domain}. Error: {e}"}, status=500)


@require_POST
def ip_geolocation(request):
    """
    Gets geolocation information for an IP address using a free API.
    """
    try:
        data = json.loads(request.body)
        ip_address = data.get('ip_address')
        if not ip_address:
            return JsonResponse({'error': 'IP address is required'}, status=400)

        # Using the ip-api.com service
        response = requests.get(f'http://ip-api.com/json/{ip_address}')
        response.raise_for_status() # Raise an exception for bad status codes
        geo_data = response.json()
        
        if geo_data.get('status') == 'fail':
            return JsonResponse({'error': geo_data.get('message', 'Failed to geolocate IP.')}, status=404)

        return JsonResponse(geo_data)
    except requests.exceptions.RequestException as e:
        return JsonResponse({'error': f"API request failed: {e}"}, status=503)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

# --- Monitoring Data API Endpoint ---

def get_network_connections(request):
    """
    Gets a list of active network connections using psutil.
    """
    try:
        connections = psutil.net_connections(kind='inet')
        conn_data = []
        for conn in connections:
            # We only care about established connections with a remote address
            if conn.status == 'ESTABLISHED' and conn.raddr:
                try:
                    proc = psutil.Process(conn.pid) if conn.pid else None
                    proc_name = proc.name() if proc else 'N/A'
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    proc_name = 'N/A'
                
                conn_data.append({
                    'local_addr': f"{conn.laddr.ip}:{conn.laddr.port}",
                    'remote_addr': f"{conn.raddr.ip}:{conn.raddr.port}",
                    'status': conn.status,
                    'pid': conn.pid or 'N/A',
                    'process_name': proc_name
                })
        return JsonResponse({'connections': conn_data})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
