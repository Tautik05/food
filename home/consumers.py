# consumers.py

from channels.generic.websocket import AsyncWebsocketConsumer
import json

class OrderConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.delivery_partner_group = f"delivery_partner_{self.scope['user'].id}"
        await self.channel_layer.group_add(self.delivery_partner_group, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.delivery_partner_group, self.channel_name)

    # Send order assignment to the WebSocket
    async def send_order_assignment(self, order_id):
        await self.send(text_data=json.dumps({
            'order_id': order_id,
        }))
        
    # A method to trigger when an order is assigned
    async def new_order_assigned(self, order_id):
        await self.channel_layer.group_send(
            self.delivery_partner_group,
            {
                'type': 'send_order_assignment',
                'order_id': order_id,
            }
        )
