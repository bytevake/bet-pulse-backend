from django.db import models
from useraccounts.models import UserAccounts

# Create your models here.
class PersonalBets(models.Model):
    """
    Holds Info About Personal Bets
    """
    outcome_choices = (
        ("better", "better"),
        ("against", "against"),
        ("none", "none"),
        ("pending", "pending"),
        ("confirmed", "confirmed"),
        ("cancelled", "cancelled")
    )
    amount_placed = models.DecimalField(max_digits=14, decimal_places=2,
        default=0.0)
    posiible_win = models.DecimalField(max_digits=14, decimal_places=2,
        default=0.0)
    witness_amount = models.DecimalField(max_digits=14, decimal_places=2,
        default=0.0)
    trans_amount = models.DecimalField(max_digits=14, decimal_places=2,
        default=0.0)
    date_time = models.DateTimeField(auto_now=True)
    end_time = models.DateTimeField(null=True)
    description = models.TextField(null=True, blank=False)
    outcome = models.CharField(max_length=12, choices=outcome_choices,
        default="pending")


class AgainstPersonalBets(models.Model):
    """
    Holds Info of User Betting Against The Bet Owner
    """
    bet_id = models.OneToOneField(PersonalBets, on_delete=models.DO_NOTHING,
        null=True)
    against = models.ForeignKey(UserAccounts, on_delete=models.DO_NOTHING,
        null=True)
    amount_placed = models.DecimalField(max_digits=14, decimal_places=2,
        default=0.0)
    trans_amount = models.DecimalField(max_digits=14, decimal_places=2,
        default=0.0)
    confirmation = models.BooleanField(default=False)
    date_time = models.DateTimeField(auto_now=True)


class WitnessPersonalBets(models.Model):
    """
    Holds Info of User Betting Against The Bet Owner
    """
    bet_id = models.OneToOneField(PersonalBets, on_delete=models.DO_NOTHING,
        null=True)
    witness = models.ForeignKey(UserAccounts, on_delete=models.DO_NOTHING,
        null=True)
    amount = models.DecimalField(max_digits=14, decimal_places=2,
        default=0.0)
    confirmation = models.BooleanField(default=False)
    date_time = models.DateTimeField(auto_now=True)


class BetterPersonalBets(models.Model):
    """
    Holds Information About the Better:
    One initiating the Bet
    """
    bet_id = models.OneToOneField(PersonalBets, on_delete=models.DO_NOTHING,
        null=True)
    better = models.ForeignKey(UserAccounts, on_delete=models.DO_NOTHING,
        null=True)
    better_confirm = models.BooleanField(default=False)
    amount_placed = models.DecimalField(max_digits=14, decimal_places=2,
        default=0.0)
    trans_amount = models.DecimalField(max_digits=14, decimal_places=2,
        default=0.0)