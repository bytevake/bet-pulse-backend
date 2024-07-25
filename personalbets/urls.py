from django.urls import path
from .views import AgainstConfrimAPIView, WitnessConfrimAPIView
from .views import PersonalBetAPIView, GetPersonalAPIView


urlpatterns = [
    path("placebet/", PersonalBetAPIView.as_view(), name="add_game"),
    path("against-confirm/", AgainstConfrimAPIView.as_view(), name="add_game"),
    path("witness-confirm/", WitnessConfrimAPIView.as_view(), name="place_bet"),
    path("notifications/<int:user_id>/", GetPersonalAPIView.as_view(), name="notifiers"),
]