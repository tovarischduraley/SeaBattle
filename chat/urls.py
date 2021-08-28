from django.urls import path

from . import views

urlpatterns = [
    path('', views.chat_index, name='index'),
    path('<str:room_name>/', views.room, name='room'),
]