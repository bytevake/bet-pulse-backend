from django.db import models
from useraccounts.models import UserAccounts
# Create your models here.
class Games(models.Model):
    """
    Will hold info about the games one can place bets on
    """
    game_status = (
        ("Active", "Active"),
        ("Inactive", "Inactive"),
    )
    game_outcomes = (
        ("Home", "Home"),
        ("Away", "Away"),
        ("Draw", "Draw"),
    )

    home = models.CharField(max_length=50, null=True, blank=False)
    away = models.CharField(max_length=50, null=True, blank=False)
    # TODO add setters to do validation
    home_odds = models.DecimalField(max_digits=5, decimal_places=3,
                                    null=True, blank=False)
    away_odds = models.DecimalField(max_digits=5, decimal_places=3,
                                    null=True, blank=False)
    draw_odds = models.DecimalField(max_digits=5, decimal_places=3,
                                    null=True, blank=False)
    game_date = models.DateTimeField(null=True, blank=False)
    status = models.CharField(max_length=10, choices=game_status,
                               default="Active")
    outcome = models.CharField(max_length=4, choices=game_outcomes,
                               null=True, blank=False)
    
class PlacedBets(models.Model):
    """
    Will hold info about Bets A User Has Placed
    """
    place_options = (
        ("Home", "Home"),
        ("Away", "Away"),
        ("Draw", "Draw"),
    )
    bet_outcomes = (
        ("Win", "Win"),
        ("Pending", "Pending"),
        ("Lose", "Lose"),
    )
    bet_statuses = (
        ("Active", "Active"),
        ("Inactive", "InActive"),
    )

    user_id = models.ForeignKey(UserAccounts, on_delete=models.DO_NOTHING,
                                null=True, blank=False)
    game_id = models.ForeignKey(Games, on_delete=models.DO_NOTHING,
                                null=True, blank=False)
    placed_bet = models.CharField(max_length=5, choices=place_options,
                                  null=True, blank=False)
    placed_amount = models.DecimalField(max_digits=14, decimal_places=2,
                                        null=True, blank=False)
    possible_win = models.DecimalField(max_digits=14, decimal_places=2,
                                       null=True, blank=False)
    bet_outcome = models.CharField(max_length=8, choices=bet_outcomes,
                                   null=True, blank=False)
    bet_status = models.CharField(max_length=10, choices=bet_statuses,
                                  default="active")