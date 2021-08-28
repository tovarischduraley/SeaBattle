from django.urls import path
from .views import *

urlpatterns = [
    path('', game_room, name='game_room'),
]
