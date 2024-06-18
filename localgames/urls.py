from django.urls import path
from .views import GamesAPIView

urlpatterns = [
    path("", GamesAPIView.as_view(), name="get_all_games"),
    path("add-game/", GamesAPIView.as_view(), name="add_game"),
]