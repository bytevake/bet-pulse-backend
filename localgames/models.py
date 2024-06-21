from django.db import models
from useraccounts.models import UserAccounts
# Create your models here.
class Games(models.Model):
    """
    Will hold info about the games one can place bets on
    """
    game_outcomes = (
        ("Home", "Home"),
        ("Away", "Away"),
        ("Draw", "Draw"),
        ("Pending", "Pending"),
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
    # true if game is active: user can still bet on game
    status = models.BooleanField(default=True)
    outcome = models.CharField(max_length=7, choices=game_outcomes,
                               default="Pending", blank=False)
    
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
    # true if trans involved loan
    on_loan = models.BooleanField(default=False)
    # TODO validation if on loan is True
    # holds loan amount
    loan_amount = models.DecimalField(max_digits=14, decimal_places=2,
                                       null=True, blank=False)
    # holds the loan rate charged
    loan_irt = models.DecimalField(max_digits=14, decimal_places=2,
                                       null=True, blank=False)
    # holds loan amount of the transaction including interest
    total_loan = models.DecimalField(max_digits=14, decimal_places=2,
                                       null=True, blank=False)