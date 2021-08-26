import json
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from django.contrib.auth.models import User

from .models import Message


class ChatConsumer(WebsocketConsumer):

    def fetch_messages(self, data):
        print('fetching')
        messages = Message.objects.order_by('timestamp').all()[:10]
        content = {
            'command': 'messages',
            'messages': self.messages_to_json(messages)
        }
        print("   ", content['messages'][0]['content'])
        print('fetched')
        self.send_message(content)

    def new_message(self, data):
        author_user = User.objects.filter(username=self.scope['user']).first()
        message = Message.objects.create(
            author=author_user,
            content=data['message']
        )

        content = {
            'command': 'new_message',
            'message': self.message_to_json(message)
        }

        return self.send_chat_message(content)

    def messages_to_json(self, messages):
        result = []
        for message in messages:
            result.append(self.message_to_json(message))
        return result

    def message_to_json(self, message):
        return {
            'author': message.author.username,
            'content': message.content,
            'timestamp': str(message.timestamp)
        }

    commands = {
        'fetch_messages': fetch_messages,
        'new_message': new_message
    }

    def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = 'chat_%s' % self.room_name

        # Join room group
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )

        self.accept()

    def disconnect(self, close_code):
        # Leave room group
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    def receive(self, text_data):
        data = json.loads(text_data)
        print('receiving')
        self.commands[data['command']](self, data)
        print('received')

    def send_chat_message(self, message):
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message
            }
        )

    def send_message(self, message):
        print('sending message')
        print(json.dumps(message))
        self.send(text_data=json.dumps(message))
        print('message sent')

    # Receive message from room group
    def chat_message(self, event):
        print('sending message')
        message = event['message']
        print(message)
        self.send(text_data=json.dumps(message))
        print('message sent')
