from django.contrib.auth.models import User
from django.db import models
from enum import Enum
import pickle


class Game(models.Model):
    group_channel_name = models.CharField(max_length=255)


class Player(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    is_playing = models.BooleanField()
    is_online = models.BooleanField()
    game_room = models.ForeignKey(Game, related_name='players', on_delete=models.SET_NULL, null=True)
    channel_name = models.CharField(max_length=255)


class GameState(models.Model):
    state = models.OneToOneField(Game, related_name='game', on_delete=models.CASCADE)
    whos_turn = models.ForeignKey(Player, related_name='game_state', on_delete=models.CASCADE)
    bf1_owner = models.ForeignKey(Player, related_name='bf1_owner_game_state', on_delete=models.CASCADE)
    bf2_owner = models.ForeignKey(Player, related_name='bf2_owner_game_state', on_delete=models.CASCADE)
    bf1 = models.CharField(max_length=100)
    bf2 = models.CharField(max_length=100)


class Cell(Enum):
    EMPTY_SHOTED = 1
    EMPTY_NOT_SHOTED = 2
    SHIP_SHOTED = 3
    SHIP_NOT_SHOTED = 4
    SHIP_DEAD = 5


class BattleField:
    def __init__(self):
        self.field = [[Cell.EMPTY_NOT_SHOTED for i in range(10)] for j in range(10)]

    def dump(self, name):
        with open(name) as f:
            pickle.dump(self.field, f)

    def load(self, name):
        with open(name) as f:
            self.field = pickle.load(f)
