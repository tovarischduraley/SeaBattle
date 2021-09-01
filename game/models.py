from django.contrib.auth.models import User
from django.db import models
from enum import Enum
import pickle


class Game(models.Model):
    group_channel_name = models.CharField(max_length=255)

    def __str__(self):
        return f'{self.state.bf1_owner} + {self.state.bf2_owner} game'


class Player(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    is_playing = models.BooleanField(default=False)
    is_online = models.BooleanField(default=False)
    game = models.ForeignKey(Game, related_name='players', on_delete=models.SET_NULL, null=True, default=None,
                             blank=True)
    channel_name = models.CharField(max_length=255)

    def __str__(self):
        return self.user.username


class GameState(models.Model):
    name = models.CharField(max_length=100, default='GAME_NOT_STARTED')
    game = models.OneToOneField(Game, related_name='state', on_delete=models.CASCADE)
    whos_turn = models.ForeignKey(Player, related_name='game_state', on_delete=models.CASCADE)
    bf1_owner = models.ForeignKey(Player, related_name='bf1_owner_game_state', on_delete=models.CASCADE)
    bf2_owner = models.ForeignKey(Player, related_name='bf2_owner_game_state', on_delete=models.CASCADE)
    bf1 = models.CharField(max_length=100)
    bf2 = models.CharField(max_length=100)

    def __str__(self):
        return f'{self.bf1_owner} + {self.bf2_owner} game state'


class Cell(Enum):
    EMPTY_NOT_SHOTED = 0
    EMPTY_SHOTED = 1
    SHIP_NOT_SHOTED = 2
    SHIP_SHOTED = 3
    SHIP_DEAD = 4


class BattleField:
    def __init__(self):
        self.field = [[Cell.EMPTY_NOT_SHOTED.name for i in range(10)] for j in range(10)]
        self.ships = [4, 3, 2, 1]

    def dump(self, name):
        with open(f'bf_dumps/{name}', 'wb') as f:
            pickle.dump([self.field, self.ships], f)
        f.close()

    def load(self, name):
        with open(f'bf_dumps/{name}', 'rb') as f:
            self.field = pickle.load(f)[0]
        f.close()

        with open(f'bf_dumps/{name}', 'rb') as f:
            self.ships = pickle.load(f)[1]
        f.close()
