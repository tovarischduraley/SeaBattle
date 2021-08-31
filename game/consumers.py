import json
import random

from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from django.contrib.auth.models import User
from chat.models import Message
from .utils import create_game_name, message_to_json, messages_to_json
from .models import Player, Game, GameState, BattleField


class GameConsumer(WebsocketConsumer):

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
            player.channel_name = self.channel_name
            player.is_online = True
            player.save()

            if player.is_playing:
                # reconnect to the game
                game = player.game
                async_to_sync(self.channel_layer.group_add)(
                    game.group_channel_name,
                    self.channel_name
                )

                bf = BattleField()

                if player == game.state.bf1_owner:
                    name = game.state.bf1
                    opponent = game.state.bf2_owner
                    opponent_name = game.state.bf2
                else:
                    name = game.state.bf2
                    opponent = game.state.bf1_owner
                    opponent_name = game.state.bf1

                bf.load(name)
                player_bf = bf.field
                player_ships = bf.ships

                bf.load(opponent_name)
                opponent_bf = bf.field
                opponent_ships = bf.ships

                if player_ships != [0, 0, 0, 0]:
                    message = "Place your ships to start play"
                    self.info_message(self.channel_name, message)
                elif opponent_ships != [0, 0, 0, 0]:
                    message = "Wait for your opponent's filled field"
                    self.info_message(self.channel_name, message)
                else:
                    self.say_whos_turn(player, opponent, game.state)

                self.load_battle_field(self.channel_name, player_bf, player_ships, opponent_bf)

            else:
                # search opponent or wait for opponent
                opponent = Player.objects.filter(is_online=True, is_playing=False).exclude(user=player.user).first()
                if opponent:
                    game = self.create_game(player, opponent)

                    bf = BattleField()

                    bf.dump(name=game.state.bf1)
                    bf.dump(name=game.state.bf2)

                    player_bf = bf.field
                    player_ships = bf.ships
                    opponent_bf = bf.field
                    opponent_ships = bf.ships

                    async_to_sync(self.channel_layer.group_add)(
                        game.group_channel_name,
                        self.channel_name
                    )
                    async_to_sync(self.channel_layer.group_add)(
                        game.group_channel_name,
                        opponent.channel_name,
                    )

                    self.load_battle_field(self.channel_name, player_bf, player_ships, opponent_bf)
                    self.load_battle_field(opponent.channel_name, opponent_bf, opponent_ships, player_bf)
                    message = "Place your ships to start play"
                    async_to_sync(self.channel_layer.group_send)(
                        game.group_channel_name,
                        {
                            'type': 'event_message',
                            'message': {
                                'command': 'info_message',
                                'message': message
                            }
                        }
                    )
                    self.info_message(player, message)

                else:
                    # wait for opponent
                    message = "Let's wait for the opponent, you're not going to play alone, are you?"
                    self.info_message(player, message)

            self.accept()


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
        for command in data['commands']:
            self.commands[command](self, data)

    def fetch_messages(self, data):
        player = Player.objects.filter(user=self.scope['user']).first()
        messages = Message.objects.filter(game_room=player.game).order_by('-timestamp').all()[:10]
        content = {
            'command': 'messages',
            'messages': messages_to_json(reversed(messages))
        }
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

    def load_battle_field(self, channel_name, bf1, ships1, bf2):
        async_to_sync(self.channel_layer.send)(
            channel_name,
            {
                'type': 'event_message',
                'message': {
                    'command': 'load_bfs',
                    'my_bf': bf1,
                    'my_ships': ships1,
                    'opponent_bf': bf2,
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

    def event_message(self, event):
        message = event['message']
        self.send(text_data=json.dumps(message))

    def send_message(self, message):
        self.send(text_data=json.dumps(message))

    def place_ship(self, data):
        print('place_ship')
        player = Player.objects.filter(user=self.scope['user']).first()
        state = player.game.state
        if player == state.bf1_owner:
            name = state.bf1
            opponent = state.bf2_owner
            opponent_name = state.bf2
        else:
            opponent = state.bf1_owner
            name = state.bf2
            opponent_name = state.bf1

        new_field = data['message']['my_bf']
        placed_ship_len = data['message']['placed_ship_len']

        bf = BattleField()
        bf.load(name)
        new_ships = bf.ships
        new_ships[placed_ship_len - 1] -= 1

        new_bf = BattleField()
        new_bf.field = new_field
        new_bf.ships = new_ships
        new_bf.dump(name)
        new_bf.load(name)

        new_field = new_bf.field
        new_ships = new_bf.ships
        bf.load(opponent_name)
        opponent_field = bf.field

        self.load_battle_field(player.channel_name, new_field, new_ships, opponent_field)
        if new_ships == [0, 0, 0, 0]:
            print('123')
            self.change_game_state(player, opponent, state)

    def change_game_state(self, player, opponent, state):
        print('change_game_state')
        if state.name == 'WAITING_FOR_OPPONENT':
            state.name = 'GAME_STARTED'
            state.save()
            self.say_whos_turn(player, opponent, state)
            # self.start_game()

        if state.name == 'GAME_NOT_STARTED':
            state.name = 'WAITING_FOR_OPPONENT'
            state.save()
            message = "Wait for your opponent's filled field"
            self.info_message(player, message)


    def say_whos_turn(self, player, opponent, state):
        print('say_whos_turn')
        if player == state.whos_turn:
            message = "Your turn! Shoot!"
            self.info_message(player, message)
            message = "Wait for your opponent turn"
            self.info_message(opponent, message)
        else:
            message = "Your turn! Shoot!"
            self.info_message(opponent, message)
            message = "Wait for your opponent turn"
            self.info_message(player, message)

    def start_game(self):

        pass

    def info_message(self, player, message):
        print('info_message')
        async_to_sync(self.channel_layer.send)(
            player.channel_name,
            {
                'type': 'event_message',
                'message': {
                    'command': 'info_message',
                    'message': message
                }
            }
        )

    commands = {
        'fetch_messages': fetch_messages,
        'new_message': new_message,
        'place_ship': place_ship,
    }
