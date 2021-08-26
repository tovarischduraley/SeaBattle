from django.contrib.auth.models import User
from django.db import models

# from game.models import Player, GameRoom


class Message(models.Model):
    author = models.ForeignKey(User, related_name='author_messages', on_delete=models.CASCADE)
    # game_room = models.ForeignKey(GameRoom, related_name='room_messages', on_delete=models.CASCADE, null=True,
    #                               blank=True)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.author.username

    # def last_10_messages(self):
    #     return Message.objects.order_by('-timestamp').all()[:10]
