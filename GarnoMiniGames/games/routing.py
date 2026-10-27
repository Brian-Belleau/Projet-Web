from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/games/premier-clic/(?P<room_name>\w+)/$', consumers.PremierClicConsumer.as_asgi()),
    re_path(r'ws/games/tic-tac-toe/(?P<room_name>\w+)/$', consumers.TicTacToeConsumer.as_asgi()),
    re_path(r'ws/games/connect-4/(?P<room_name>\w+)/$', consumers.Connect4Consumer.as_asgi()),
]
