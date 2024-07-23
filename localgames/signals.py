from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Games, PlacedBets
from .helpers import update_normal_bet, update_loan_bet

@receiver(post_save, sender=Games)
def update_bets(sender, instance, created, **kwargs):
    """
    Used To Create An Account for Non Staff Users
    """
    # ignores creation of instance
    if not created:
        if instance and instance.outcome != "Pending":
            # get all bets associated with this game
            placed_bets = PlacedBets.objects.filter(game_id=instance.id,
                bet_outcome="Pending")
            on_loans = placed_bets.filter(on_loan=True)
            normal_bets = placed_bets.filter(on_loan=False)

            for norm_bet in normal_bets:
                update_normal_bet(norm_bet, instance.outcome)
            
            for loan_bet in on_loans:
                update_loan_bet(loan_bet, instance.outcome)