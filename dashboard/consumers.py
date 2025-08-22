# dashboard/consumers.py

import asyncio
import json
import psutil
from channels.generic.websocket import AsyncWebsocketConsumer

class NetworkMonitorConsumer(AsyncWebsocketConsumer):
    """
    A WebSocket consumer that streams network I/O stats.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.monitoring_task = None

    async def connect(self):
        await self.accept()
        # Start a background task to send network stats periodically
        self.monitoring_task = asyncio.create_task(self.send_network_stats())

    async def disconnect(self, close_code):
        # Stop the background task when the client disconnects
        if self.monitoring_task:
            self.monitoring_task.cancel()

    async def send_network_stats(self):
        """
        Periodically fetches and sends network I/O stats.
        """
        # Get initial stats
        last_stat = psutil.net_io_counters()

        while True:
            try:
                await asyncio.sleep(2) # Update interval in seconds
                
                current_stat = psutil.net_io_counters()
                
                # Calculate the difference since the last measurement
                bytes_sent = current_stat.bytes_sent - last_stat.bytes_sent
                bytes_recv = current_stat.bytes_recv - last_stat.bytes_recv
                
                # Update the last stat for the next calculation
                last_stat = current_stat

                await self.send(text_data=json.dumps({
                    'bytes_sent': bytes_sent,
                    'bytes_recv': bytes_recv,
                }))
            except asyncio.CancelledError:
                # This happens when the disconnect method cancels the task
                break
            except Exception as e:
                # Handle potential errors without crashing the loop
                await self.send(text_data=json.dumps({'error': str(e)}))
                break
