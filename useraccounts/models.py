from django.db import models
from accounts.models import CustomUser
# Create your models here.


class UserAccounts(models.Model):
    """
    Holds A Users Account Balance
    """
    user_id = models.OneToOneField(CustomUser, on_delete=models.CASCADE,
        primary_key=True,)
    balance = models.DecimalField(max_digits=14, decimal_places=2, default=0.0)


class UserTransactions(models.Model):
    """
    Will hold Records for activities of user account
    such as:
    Withdrawals, Deposits, Increments and Decrements from Placed Bets
    """
    # holds the type of transactions
    trans_types = (
        ("Deposit", "Deposit"),
        ("Withdrawal", "Withdrawal"),
        ("BetPlacement", "BetPlacement"),
        ("LoanBetPlacement", "LoanBetPlacement"),
        ("BetWin", "BetWin"),
    )
    user_id = models.ForeignKey(UserAccounts,on_delete=models.DO_NOTHING)
    # negative value if leads to deduction in account balance
    trans_amount = models.DecimalField(max_digits=14, decimal_places=2,
                                       null=True, blank=False)
    trans_nature = models.CharField(max_length=20, choices=trans_types,
                                    null=True, blank=False)
    # holds the account balance after transaction
    account_balance = models.DecimalField(max_digits=14, decimal_places=2,
                                          null=True, blank=False)