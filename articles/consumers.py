# import json
# from channels.generic.websocket import AsyncWebsocketConsumer

# class NotificationConsumer(AsyncWebsocketConsumer):
#     async def connect(self):
#         self.user = self.scope["user"]
#         if self.user.is_authenticated:
#             self.group_name = f"user_{self.user.id}"
#             await self.channel_layer.group_add(self.group_name, self.channel_name)
#             await self.accept()
#             print(f"✅ {self.user} connected to {self.group_name}")
#         else:
#             await self.close()

#     async def disconnect(self, close_code):
#         if self.user.is_authenticated:
#             await self.channel_layer.group_discard(self.group_name, self.channel_name)
#             print(f"❌ {self.user} disconnected from {self.group_name}")

#     async def send_notification(self, event):
#         await self.send(text_data=json.dumps({
#             "message": event["message"]
#         }))



import json
from channels.generic.websocket import AsyncWebsocketConsumer

class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]
        print("Connecting user:", self.user, "authenticated?", self.user.is_authenticated)

        if self.user.is_authenticated:
            self.group_name = f"user_{self.user.id}"
            await self.channel_layer.group_add(self.group_name, self.channel_name)
            await self.accept()
            print(f"✅ {self.user} connected to {self.group_name}")
        else:
            print("❌ User not authenticated, closing connection")
            await self.close()

    async def disconnect(self, close_code):
        if hasattr(self, 'group_name'):
            await self.channel_layer.group_discard(self.group_name, self.channel_name)
            print(f"❌ {self.user} disconnected from {self.group_name}")

    async def send_notification(self, event):
        await self.send(text_data=json.dumps({
            "message": event["message"]
        }))


        