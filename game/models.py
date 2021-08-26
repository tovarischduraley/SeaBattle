from django.contrib.auth.models import User
from django.db import models


class GameRoom(models.Model):
    name = models.CharField(max_length=20)

    # player1 = models.ForeignKey(Player, on_delete=models.CASCADE)
    # player2 = models.ForeignKey(Player, on_delete=models.CASCADE)


class Player(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    game_room = models.ForeignKey(GameRoom, related_name='players', on_delete=models.SET_NULL)


class BattleField(models.Model):
    pass
