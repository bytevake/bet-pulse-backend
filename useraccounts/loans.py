"""
Will handle all matters pertaining to users loans'
"""

from betting_pulse.constants import MIN_TRANS, LOAN_THRES
from useraccounts.models import UserTransactions, UserAccounts
from django.db.models import Sum


def is_loan_eligible(user_id, req_amount):
    """
    Used to check if a user is eligible for a loan
    Return:
        True: If User is eligible for loan
        False: If User is not eligible for loan
    """
    # user has loan
    if UserAccounts.objects.get(user_id=user_id).balance < 0:
        return False
    
    # holds positive trans by a user
    pos_trans = UserTransactions.objects.filter(user_id=user_id, trans_nature="Deposit").count() +\
        UserTransactions.objects.filter(user_id=user_id, trans_nature="BetWin").count()
    
    if pos_trans < MIN_TRANS:
        return False
    
    total_dep = UserTransactions.objects.filter(user_id=user_id, trans_nature="Deposit").aggregate(total_deposit=Sum('trans_amount'))
    total_win = UserTransactions.objects.filter(user_id=user_id, trans_nature="BetWin").aggregate(total_win=Sum('trans_amount'))
    
    if total_win["total_win"] is None:
        # user has never won any bet
        return False
    
    total_pos = total_dep["total_deposit"] + total_win["total_win"]

    if (req_amount * 3) > total_pos:
        return False
    
    return True