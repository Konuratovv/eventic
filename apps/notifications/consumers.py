import json

import jwt
from asgiref.sync import sync_to_async, async_to_sync
from channels.generic.websocket import WebsocketConsumer, AsyncWebsocketConsumer
from apps.notifications.tasks import send_notification_task
from apps.profiles.models import User
from config.settings.base import SECRET_KEY


# class UserConsumer(WebsocketConsumer):
#
#     def connect(self):
#         self.room_name = "test_consumer"
#         self.room_group_name = "test_consumer_group"
#
#         async_to_sync(self.channel_layer.group_add)(
#             self.room_name, self.room_group_name
#         )
#         self.accept()
#         self.send(text_data=json.dumps({'status': 'connected'}))
#
#     def receive(self, text_data):
#         print(text_data)
#         self.send(text_data=json.dumps({'status': 'we got you'}))
#
#     def send_notification(self, event):
#         print('send notification')
#         data = json.loads(event.get('value'))
#         self.send(text_data=json.dumps({'users': data}))
#         print('send notification')

# async def websocket_receive(self, text_data):
#     print(text_data)
#
#     await self.send(json.dumps(text_data))
#     # await self.send(json.dumps({'text_data': 'Ваше сообщение было успешно получено и обработано.'}))

# async def websocket_connect(self, message):
#     pass
#
# async def connect(self):
#     pass
#
# async def accept(self, subprotocol=None):
#     pass
#
# async def receive(self, text_data=None, bytes_data=None):
#     pass
#
# async def send(self, text_data=None, bytes_data=None, close=False):
#     pass
#
# async def close(self, code=None):
#     pass
#
# async def websocket_disconnect(self, message):
#     pass
#
# async def disconnect(self, code):
#     pass


class NotificationConsumer(AsyncWebsocketConsumer):
    user_connections = {}

    @sync_to_async
    def get_user(self, user_id):
        return User.objects.get(id=user_id)

    async def connect(self):
        await self.accept()
        token = self.scope['query_string'].decode()
        tk = token.split('=')[1]
        decoded_token = jwt.decode(tk, SECRET_KEY, algorithms=['HS256'])
        user = await self.get_user(decoded_token.get("user_id"))
        self.user_connections[str(user)] = self.channel_name
        await self.channel_layer.group_add("notifications", self.channel_name)

    async def disconnect(self, event):
        token_to_remove = []
        for token, channel_name in self.user_connections.items():
            if channel_name == self.channel_name:
                token_to_remove.append(token)
        del self.user_connections[token_to_remove[0]]

    # async def disconnect(self, code):
    #     tokens_to_remove = []
    #     for token, channel_name in self.user_connections.items():
    #         if channel_name == self.channel_layer:
    #             tokens_to_remove.append(token)
    #
    #     if tokens_to_remove:  # Проверяем, что список не пустой
    #         self.user_connections.pop(tokens_to_remove[0])
    #         print(self.user_connections)

    # for token, channel_name in self.user_connections.items():
    #     if channel_name == self.channel_layer:
    #         self.user_connections.pop(token)
    #         print(self.user_connections)
    #         break

    async def send_notification(self, event):
        message = event["message"]
        # print(self.channel_name)

        await self.send(
            text_data=json.dumps(
                {
                    "type": "notifications",
                    "message": message
                }
            )
        )
