import json
import jwt
from asgiref.sync import sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer

from apps.notifications.tasks import send_notifications_history
from apps.profiles.models import User
from config.settings.base import SECRET_KEY
from apps.users.utils import add_to_redis_dict, delete_from_redis_dict


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
        send_notifications_history.delay(decoded_token.get("user_id"), self.channel_name)
        add_to_redis_dict("user_connections", self.user_connections)
        await self.channel_layer.group_add("notifications", self.channel_name)

    async def disconnect(self, event):
        token_to_remove = []
        for token, channel_name in self.user_connections.items():
            if channel_name == self.channel_name:
                delete_from_redis_dict("user_connections", [token])
                token_to_remove.append(token)
        del self.user_connections[token_to_remove[0]]

    async def send_notification(self, event):
        message = event["message"]

        await self.send(
            text_data=json.dumps(
                message, ensure_ascii=False
            )
        )
