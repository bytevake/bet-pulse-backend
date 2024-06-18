from django.urls import path
from .views import GamesAPIView, PlaceBetAPIView

urlpatterns = [
    path("", GamesAPIView.as_view(), name="get_all_games"),
    path("add-game/", GamesAPIView.as_view(), name="add_game"),
    path("place-bet/", PlaceBetAPIView.as_view(), name="place_bet"),
]