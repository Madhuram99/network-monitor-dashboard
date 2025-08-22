# Network Monitor & Security Dashboard

<p align="center">
  <img src="https://img.shields.io/badge/python-3.9%2B-blue.svg" alt="Python Version">
  <img src="https://img.shields.io/badge/django-4.2%2B-green.svg" alt="Django Version">
  <img src="https://img.shields.io/badge/license-MIT-lightgrey.svg" alt="License">
</p>

A full-stack, real-time network analysis dashboard built with Django and Django Channels. This project serves as a comprehensive demonstration of core networking concepts, security fundamentals, and modern full-stack development practices, packaged into a practical and interview-ready application.

---

## Table of Contents
1. [Live Demo](#live-demo)
2. [Core Features](#core-features)
3. [Technology Stack](#technology-stack)
4. [System Architecture](#system-architecture--workflow)
5. [Code Highlights](#code-highlights--implementation-deep-dive)
6. [How to Run Locally](#how-to-run-locally)
7. [Future Improvements](#future-improvements)

---

## Live Demo

*(Here you can add a screenshot or a GIF of your running application. This is highly recommended!)*

**[Link to your live demo if you deploy it]**

---

## Core Features

This dashboard is organized into three main sections, each providing a distinct set of functionalities:

#### 实时监控 (Real-time Monitoring)
- **Live Bandwidth Monitor**: Utilizes **WebSockets** to stream and visualize real-time network upload/download speeds using **Chart.js**.
- **Active Connection Viewer**: Displays a list of all `ESTABLISHED` network connections on the server, including the process ID and name, using **`psutil`**.

#### 网络工具 (Network Utilities)
- **Ping Tool**: Sends ICMP echo requests to a host to check reachability and latency via the system's `ping` command.
- **DNS Lookup**: Resolves a domain name to its corresponding IP address.

#### 网络安全工具 (Network Security Tools)
- **Port Scanner**: Performs a basic TCP connect scan on a target IP to identify open ports.
- **SSL Certificate Checker**: Fetches and displays key details of a domain's SSL/TLS certificate.
- **IP Geolocation**: Provides geographical information for a public IP address by querying a third-party REST API.

---

## Technology Stack

| Category          | Technology                                                              | Purpose                                                                 |
| ----------------- | ----------------------------------------------------------------------- | ----------------------------------------------------------------------- |
| **Backend** | **Python 3.9+** | Core programming language.                                              |
|                   | **Django 4.2+** | High-level web framework for backend logic, routing, and API endpoints. |
|                   | **Django Channels** | Extends Django to handle WebSockets for real-time communication.        |
|                   | **Daphne** | The ASGI server required to run Django Channels.                        |
| **Frontend** | **HTML5 / CSS3** | Structure and styling of the web page.                                  |
|                   | **Tailwind CSS** | A utility-first CSS framework for rapid, responsive UI development.     |
|                   | **Vanilla JavaScript (ES6+)** | Handles all client-side interactivity, API calls, and DOM manipulation. |
|                   | **Chart.js** | A JavaScript library for creating responsive, animated charts.          |
| **Python Libs** | **`psutil`** | Fetches system details like network connections and I/O statistics.     |
|                   | **`requests`** | Makes HTTP requests to the external IP Geolocation API.                 |
|                   | **`socket`, `subprocess`, `ssl`** | Python's built-in libraries for low-level network operations.           |

---

## System Architecture & Workflow

This project uses a client-server architecture enhanced with a real-time WebSocket layer.

1.  **Initial Request (HTTP)**: The browser requests the main page. The Daphne ASGI server routes this to Django's standard view-handling system, which renders and returns the `index.html` page.
2.  **Real-time Connection (WebSocket)**: The loaded JavaScript immediately opens a WebSocket connection to the server. Daphne routes this connection to the `NetworkMonitorConsumer` in Django Channels.
3.  **Tool Usage (Asynchronous HTTP - AJAX)**: When the user interacts with a tool (e.g., Ping), the JavaScript sends a `fetch` POST request with a JSON payload to the appropriate API endpoint. This request is handled by a standard Django view, which performs the network operation, and returns a JSON response. The frontend then updates the UI dynamically without a page reload.

---

## Code Highlights & Implementation Deep Dive

### 1. Real-time Bandwidth Monitor (`dashboard/consumers.py`)

This feature combines `asyncio` and `psutil` within a Channels consumer to provide real-time data.

```python
# dashboard/consumers.py
import asyncio
import psutil
from channels.generic.websocket import AsyncWebsocketConsumer

class NetworkMonitorConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()
        # Start a background task that runs concurrently
        self.monitoring_task = asyncio.create_task(self.send_network_stats())

    async def disconnect(self, close_code):
        self.monitoring_task.cancel() # Clean up the task on disconnect

    async def send_network_stats(self):
        last_stat = psutil.net_io_counters()
        while True:
            try:
                await asyncio.sleep(2) # Non-blocking sleep
                current_stat = psutil.net_io_counters()
                # Calculate the delta since the last reading
                bytes_sent = current_stat.bytes_sent - last_stat.bytes_sent
                bytes_recv = current_stat.bytes_recv - last_stat.bytes_recv
                last_stat = current_stat
                # Send data to the client
                await self.send(text_data=json.dumps({
                    'bytes_sent': bytes_sent, 'bytes_recv': bytes_recv,
                }))
            except asyncio.CancelledError:
                break
```

### 2. SSL Certificate Checker (`dashboard/views.py`)

This view demonstrates a low-level network interaction to perform a TLS handshake.

```python
# dashboard/views.py
import ssl
import socket
from django.http import JsonResponse

def ssl_cert_check(request):
    # ...
    try:
        context = ssl.create_default_context()
        with socket.create_connection((domain, 443)) as sock:
            # Wrap the TCP socket in a TLS/SSL layer to perform the handshake
            with context.wrap_socket(sock, server_hostname=domain) as ssock:
                cert = ssock.getpeercert()
                # ... format and return cert as JSON ...
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
```

---

## How to Run Locally

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/your-username/network_dashboard_project.git](https://github.com/your-username/network_dashboard_project.git)
    cd network_dashboard_project
    ```

2.  **Create and activate a virtual environment:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Run database migrations:**
    ```bash
    python manage.py migrate
    ```

5.  **Run the ASGI development server:**
    ```bash
    python manage.py runserver
    ```

6.  Open your browser and navigate to `http://127.0.0.1:8000`.

---

## Future Improvements

- **Asynchronous Views**: Convert the blocking tool views (Ping, Port Scan) to be fully asynchronous using `async def` to improve performance.
- **Historical Data & Visualization**: Store monitoring data in a database (e.g., PostgreSQL) to create historical charts.
- **Traceroute Tool**: Add a traceroute utility to visualize the network path to a destination host.
- **User Authentication**: Implement a user login system for personalized dashboards.
- **Advanced Scanning**: Integrate a more powerful library like `python-nmap` or `scapy` to allow for different types of port scans (SYN, UDP, etc.).

