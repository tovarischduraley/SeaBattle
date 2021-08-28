# chat/views.py
from django.shortcuts import render

def chat_index(request):
    return render(request, 'chat/../game/templates/game/index.html', {})

def room(request, room_name):
    return render(request, 'chat/../game/templates/game/room.html', {
        'room_name': room_name
    })