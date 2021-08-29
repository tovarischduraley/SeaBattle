import json
import random

from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from django.contrib.auth.models import User
from chat.models import Message
from .utils import create_game_name, message_to_json, messages_to_json
from .models import Player, Game, GameState, BattleField


class ChatConsumer(WebsocketConsumer):

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

                    game = self.create_game(player, opponent)

                    player_bf, opponent_bf = self.create_battle_fields(game)

                    async_to_sync(self.channel_layer.group_add)(
                        game.group_channel_name,
                        [player.channel_name, opponent.channel_name]
                    )

                    async_to_sync(self.channel_layer.group_send)(
                        game.group_channel_name,
                        {
                            "type": "send_message",
                            "message": {
                                'command': 'set_game',
                                'player1_bf': player_bf,
                                'player2_bf': opponent_bf,
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

    def fetch_messages(self, data):
        # print('fetching')
        player = Player.objects.filter(user=self.scope['user']).first()
        messages = Message.objects.filter(game_room=player.game).order_by('-timestamp').all()[:10]
        content = {
            'command': 'messages',
            'messages': messages_to_json(reversed(messages))
        }
        # print('fetched')
        self.send_message(content)

    def new_message(self, data):
        player = Player.objects.filter(user=self.scope['user']).first()
        if player.game:
            author = player.user
            message = Message.objects.create(
                author=author,
                game_room=player.game,
                content=data['message']
            )

            content = {
                'command': 'new_message',
                'group_channel_name': player.game.group_channel_name,
                'message': message_to_json(message)
            }

            return self.send_chat_message(content)
        return self.send_message(
            {
                'command': 'error',
                'message': 'Your game is not ready yet. So, wait for your opponent'
            }
        )

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

        return game

    def create_battle_fields(self, game):

        battle_field1 = BattleField()
        battle_field2 = BattleField()

        battle_field1.dump(name=game.state.bf1)
        battle_field2.dump(name=game.state.bf2)

        return battle_field1, battle_field2


    def start_game(self):
        pass

    def load_game(self):
        pass


    def send_chat_message(self, message):
        async_to_sync(self.channel_layer.group_send)(
            message['group_channel_name'],
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
        # print(message)
        self.send(text_data=json.dumps(message))
        # print('CHAT_MESSAGE message sent')

    commands = {
        'fetch_messages': fetch_messages,
        'new_message': new_message,
        'start_game': start_game
    }
