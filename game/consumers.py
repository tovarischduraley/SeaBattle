import json
import random

from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from django.contrib.auth.models import User
from chat.models import Message
from .utils import create_game_name, message_to_json, messages_to_json
from .models import Player, Game, GameState


class ChatConsumer(WebsocketConsumer):

    def fetch_messages(self, data):
        # print('fetching')
        messages = Message.objects.order_by('-timestamp').all()[:10]
        content = {
            'command': 'messages',
            'messages': messages_to_json(reversed(messages))
        }
        # print('fetched')
        self.send_message(content)

    def new_message(self, data):
        author_user = User.objects.filter(username=self.scope['user']).first()
        message = Message.objects.create(
            author=author_user,
            content=data['message']
        )

        content = {
            'command': 'new_message',
            'message': message_to_json(message)
        }

        return self.send_chat_message(content)

    # def wait_for_opponent(self):
    #     pass

    def create_game(self, player1, player2):
        game_name = str(create_game_name())
        game = Game.objects.create(group_channel_name=game_name)
        GameState.objects.create(
            game=game,
            whos_turn=random.choice([player1, player2]),
            bf1_owner=player1,
            bf2_owner=player2,
            bf1=f'{game_name}_1',
            bf2=f'{game_name}_2',
        )
        player1.game = game
        player1.is_playing = True
        player1.save()

        player2.game = game
        player2.is_playing = True
        player2.save()

        return game.group_channel_name

    def start_game(self):
        pass

    def load_game(self):
        pass

    commands = {
        'fetch_messages': fetch_messages,
        'new_message': new_message,
        'start_game': start_game
    }

    def connect(self):
        # print('connecting')
        current_user = self.scope['user']
        if current_user.is_authenticated:
            player = Player.objects.filter(user=current_user).first()
            if not player:
                player = Player.objects.create(
                    user=current_user,
                    is_online=True,
                    channel_name=self.channel_name
                )
            if player.is_playing:
                # reconnect to the game
                async_to_sync(self.channel_layer.group_add)(
                    player.game.group_channel_name,
                    self.channel_name
                )
            else:
                # search opponent or wait for opponent
                opponent = Player.objects.filter(is_online=True, is_playing=False).exclude(user=player.user).first()
                if opponent:

                    group_channel_name = self.create_game(player, opponent)

                    async_to_sync(self.channel_layer.group_add)(
                        group_channel_name,
                        [player.channel_name, opponent.channel_name]
                    )

                    # async_to_sync(self.channel_layer.group_add)(
                    #     group_channel_name,
                    #     opponent.channel_name
                    # )

                    async_to_sync(self.channel_layer.group_send)(
                        group_channel_name,
                        {
                            "type": "send_message",
                            "message": {
                                'request_type': 'start_game',
                                # ''GAME DATA
                            }
                        }
                    )

                else:
                    # wait for opponent
                    async_to_sync(self.channel_layer.send)(
                        self.channel_name,
                        {
                            'type': 'send_message',
                            'message': {
                                'command': 'waiting_for_opponent',
                            }
                        }
                    )

            self.accept()
            player.is_online = True
            player.save()

            # print('connected')
            # Set Online
            # Прелоадер
            # Проверить на существование
            # Если есть то переподключать

    def disconnect(self, close_code):
        player = Player.objects.filter(user=self.scope['user']).first()
        if player.game:
            async_to_sync(self.channel_layer.group_discard)(
                player.game.group_channel_name,
                self.channel_name
            )
        else:
            player.is_playing = False
        player.is_online = False
        player.save()

    def receive(self, text_data):
        data = json.loads(text_data)
        # print('receiving')
        for command in data['commands']:
            self.commands[command](self, data)
        # print('received')

    def send_chat_message(self, message):
        async_to_sync(self.channel_layer.group_send)(
            'game',
            {
                'type': 'chat_message',
                'message': message
            }
        )

    def send_message(self, message):
        # print('SEND_MESSAGE sending message')
        self.send(text_data=json.dumps(message))
        # print('SEND_MESSAGE message sent')

    def chat_message(self, event):
        # print('CHAT_MESSAGE sending message')
        message = event['message']
        print(message)
        self.send(text_data=json.dumps(message))
        # print('CHAT_MESSAGE message sent')
