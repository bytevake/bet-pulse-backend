from django.urls import path
from .views import AgainstConfrimAPIView, WitnessConfrimAPIView
from .views import PersonalBetAPIView


urlpatterns = [
    path("placebet/", PersonalBetAPIView.as_view(), name="add_game"),
    path("against-confirm/", AgainstConfrimAPIView.as_view(), name="add_game"),
    path("witness-confirm/", WitnessConfrimAPIView.as_view(), name="place_bet"),
]