from rest_framework import serializers
from .models import Games, PlacedBets


class GamesSerializer(serializers.ModelSerializer):
    game_id = serializers.IntegerField(source="id")
    class Meta:
        model = Games
        fields = ['game_id', 'home', 'away', 'home_odds', 'away_odds',
                  'draw_odds', 'game_date', 'status', 'outcome',
                  ]

class PlacedBetsSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlacedBets
        fields = ['user_id', 'game_id', 'placed_bet', 'placed_amount',
                  'possible_win', 'bet_outcome',]