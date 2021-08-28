import json
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from django.contrib.auth.models import User

from chat.models import Message
from game.models import Player


class ChatConsumer(WebsocketConsumer):

    def fetch_messages(self, data):
        print('fetching')
        messages = Message.objects.order_by('-timestamp').all()[:10]
        content = {
            'command': 'messages',
            'messages': self.messages_to_json(reversed(messages))
        }
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
            'timestamp': str(message.timestamp),
        }

    def wait_for_opponent(self):
        pass

    commands = {
        'fetch_messages': fetch_messages,
        'new_message': new_message,
    }

    def connect(self):
        print('connecting')
        current_user = self.scope['user']
        if current_user.is_authenticated:
            if Player.objects.filter(user=current_user).first():
                pass
            else:
                Player.objects.create(

                )
            # Online
            # Прелоадер
            # Проверить на существование
            # Если есть то переподключать
            #
            # Player.objects.create(user=self.scope['user'], channel_name=self.channel_name)
            async_to_sync(self.channel_layer.group_add)(
                'game',
                self.channel_name
            )

            self.accept()
            print('connected')

    def disconnect(self, close_code):
        # Online
        async_to_sync(self.channel_layer.group_discard)(
            'game',
            self.channel_name
        )

    def receive(self, text_data):
        data = json.loads(text_data)
        print('receiving')
        for command in data['commands']:
            self.commands[command](self, data)
        print('received')

    def send_chat_message(self, message):
        async_to_sync(self.channel_layer.group_send)(
            'game',
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

    def chat_message(self, event):
        print('sending message')
        message = event['message']
        print(message)
        self.send(text_data=json.dumps(message))
        print('message sent')
