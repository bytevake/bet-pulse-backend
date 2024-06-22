from django.urls import path
from .views import GamesAPIView, PlaceBetAPIView
from .views import LoanPlaceBetsAPIView, UpdateGameOutComeAPIView

urlpatterns = [
    path("", GamesAPIView.as_view(), name="get_all_games"),
    path("add-game/", GamesAPIView.as_view(), name="add_game"),
    path("update-outcome/", UpdateGameOutComeAPIView.as_view(), name="add_game"),
    path("place-bet/", PlaceBetAPIView.as_view(), name="place_bet"),
    path("loan-bet/", LoanPlaceBetsAPIView.as_view(), name="loan_bet"),
]