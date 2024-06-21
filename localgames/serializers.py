from rest_framework import serializers
from .models import Games, PlacedBets


class GamesSerializer(serializers.ModelSerializer):
    game_id = serializers.IntegerField(source="id", read_only=True)
    class Meta:
        model = Games
        fields = ['game_id', 'home', 'away', 'home_odds', 'away_odds',
                  'draw_odds', 'game_date', 'status', 'outcome',
                ]

class PlacedBetsSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlacedBets
        fields = ['user_id', 'game_id', 'placed_bet', 'placed_amount',
                  'possible_win', 'bet_outcome', 'on_loan',
                  'loan_amount', 'loan_irt',
                ]
    
    on_loan = serializers.BooleanField(read_only=True)
    loan_amount = serializers.DecimalField(max_digits=14, decimal_places=2,
        read_only=True)
    loan_irt = serializers.DecimalField(max_digits=14, decimal_places=2,
        read_only=True)
    
    def create(self, validated_data):
        """
        Create and return a new `PlacedBets` instance, given the validated data.
        """
        placed_bet = PlacedBets.objects.create(**validated_data)
        if self.context.get("loan_amount") is not None:
            placed_bet.loan_amount = self.context["loan_amount"]
            placed_bet.on_loan =  True # indicating the trans is from loan
        else:
            placed_bet.loan_amount = 0
            placed_bet.loan_irt = 0
            placed_bet.total_loan = 0
            placed_bet.on_loan = False
        placed_bet.save()
        return placed_bet