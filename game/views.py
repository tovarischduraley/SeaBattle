from django.shortcuts import render
from django.contrib.auth.decorators import login_required


@login_required
def game_room(request):
    return render(request, 'game/game_room.html')
