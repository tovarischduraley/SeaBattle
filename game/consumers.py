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
                )
            if player.is_playing:
                # reconnect to the game
                game = player.game
                async_to_sync(self.channel_layer.group_add)(
                    game.group_channel_name,
                    self.channel_name
                )
                player_bf = BattleField()
                player_bf.load(game.state.bf1)
                player_bf = player_bf.field

                opponent_bf = BattleField()
                opponent_bf.load(game.state.bf2)
                opponent_bf = opponent_bf.field

                self.load_battle_fields(player_bf, opponent_bf)

            else:
                # search opponent or wait for opponent
                opponent = Player.objects.filter(is_online=True, is_playing=False).exclude(user=player.user).first()
                if opponent:

                    game = self.create_game(player, opponent)

                    battle_field1 = BattleField()
                    battle_field2 = BattleField()

                    battle_field1.dump(name=game.state.bf1)
                    battle_field2.dump(name=game.state.bf2)

                    player_bf, opponent_bf = self.create_battle_fields(game)

                    async_to_sync(self.channel_layer.group_add)(
                        game.group_channel_name,
                        self.channel_name
                    )
                    async_to_sync(self.channel_layer.group_add)(
                        game.group_channel_name,
                        opponent.channel_name,
                    )

                    self.load_battle_fields(player_bf, opponent_bf)
                    # async_to_sync(self.channel_layer.group_send)(
                    #     game.group_channel_name,
                    #     {
                    #         'type': 'event_message',
                    #         'message': {
                    #             'command': 'start_game',
                    #             '4ship_count': 1,
                    #             '3ship_count': 2,
                    #             '2ship_count': 3,
                    #             '1ship_count': 4,
                    #         }
                    #     }
                    # )

                else:
                    # wait for opponent
                    async_to_sync(self.channel_layer.send)(
                        self.channel_name,
                        {
                            'type': 'event_message',
                            'message': {
                                'command': 'waiting_for_opponent',
                            }
                        }
                    )

            self.accept()
            player.channel_name = self.channel_name
            player.is_online = True
            player.save()


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
            bf1=f'{game_name}1',
            bf2=f'{game_name}2',
        )
        player1.game = game
        player1.is_playing = True
        player1.save()

        player2.game = game
        player2.is_playing = True
        player2.save()

        return game


    def load_battle_fields(self, bf1, bf2):
        async_to_sync(self.channel_layer.send)(
            self.channel_name,
            {
                'type': 'event_message',
                'message': {
                    'command': 'load_bfs',
                    'player1_bf': bf1,
                    # 'player1_ships': bf1,
                    'player2_bf': bf2,
                    # 'player2_ships': bf2,
                }
            }
        )

    def send_chat_message(self, message):
        async_to_sync(self.channel_layer.group_send)(
            message['group_channel_name'],
            {
                'type': 'event_message',
                'message': message
            }
        )

    def send_message(self, message):
        self.send(text_data=json.dumps(message))

    def event_message(self, event):
        message = event['message']
        self.send(text_data=json.dumps(message))

    commands = {
        'fetch_messages': fetch_messages,
        'new_message': new_message,
        'load_battle_fields': load_battle_fields
    }
