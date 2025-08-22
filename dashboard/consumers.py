# dashboard/consumers.py

import asyncio
import json
import psutil
from channels.generic.websocket import AsyncWebsocketConsumer

class NetworkMonitorConsumer(AsyncWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.monitoring_task = None

    async def connect(self):
        await self.accept()
        self.monitoring_task = asyncio.create_task(self.send_network_stats())

    async def disconnect(self, close_code):
        if self.monitoring_task:
            self.monitoring_task.cancel()

    async def send_network_stats(self):
        # FIX: Wrap the initial psutil call in a try...except block
        try:
            last_stat = psutil.net_io_counters()
        except Exception as e:
            await self.send(text_data=json.dumps({'error': f"psutil not available on this server: {e}"}))
            return # Stop the task if psutil fails

        while True:
            try:
                await asyncio.sleep(2)
                
                current_stat = psutil.net_io_counters()
                
                bytes_sent = current_stat.bytes_sent - last_stat.bytes_sent
                bytes_recv = current_stat.bytes_recv - last_stat.bytes_recv
                
                last_stat = current_stat

                await self.send(text_data=json.dumps({
                    'bytes_sent': bytes_sent,
                    'bytes_recv': bytes_recv,
                }))
            except asyncio.CancelledError:
                break
            except Exception as e:
                await self.send(text_data=json.dumps({'error': str(e)}))
                break
