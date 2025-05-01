import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from rest_framework_simplejwt.exceptions import InvalidToken
from django.contrib.auth.models import User
from .models import Message
from .serializers import MessageSerializer
from jwt import decode as jwt_decode
from django.conf import settings

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'chat_{self.room_name}'

        token = self.scope['query_string'].decode().split('=')[1]
        user = await self.get_user_from_token(token)

        if user:
            self.scope['user'] = user
            await self.channel_layer.group_add(self.room_group_name, self.channel_name)
            await self.accept()
        else:
            await self.close()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        user = self.scope["user"]
        message = await self.save_message(user, data['message'])

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': MessageSerializer(message).data
            }
        )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps(event['message']))

    @database_sync_to_async
    def get_user_from_token(self, token):
        try:
            decoded_data = jwt_decode(token, settings.SECRET_KEY, algorithms=["HS256"])
            user_id = decoded_data["user_id"]
            return User.objects.get(id=user_id)
        except (InvalidToken, User.DoesNotExist, KeyError):
            return None

    @database_sync_to_async
    def save_message(self, user, content):
        return Message.objects.create(sender=user, content=content, room_name=self.room_name)
