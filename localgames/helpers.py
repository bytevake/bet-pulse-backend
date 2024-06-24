"""
Has Reusable Methods
"""
from .models import PlacedBets
from useraccounts.serializers import UserTransSerializer
from useraccounts.models import UserAccounts

def update_normal_bet(placed_bet: PlacedBets, outcome: str):
    """
    Used to update normal bets that are not on looan
    Args:
        placed_bet(PlacedBet): The Placed bet instance
        outcome: The outcome of the game
    Return:
        None
    """
    # won the bet
    if placed_bet.placed_bet == outcome:
        prev_balance = placed_bet.user_id.balance
        new_balance = placed_bet.possible_win + placed_bet.user_id.balance
        placed_bet.bet_outcome = "Win"
        data = {
            "user_id": placed_bet.user_id,
            "trans_amount": placed_bet.possible_win,
            "trans_nature": "BetWin",
            "account_balance": new_balance
        }
        # update users transactions and user account
        serializer = UserTransSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            # update users account balance
            user_acc = UserAccounts.objects.get(user_id=placed_bet.user_id)
            user_acc.balance = new_balance
            user_acc.save()

            if prev_balance < 0:
                # user has loan, record loan payment
                if new_balance > 0:
                    # user has paid full loan
                    data = [
                        # record loan payment
                        {
                            "user_id": placed_bet.user_id,
                            "trans_amount": prev_balance,
                            "trans_nature": "LoanPayment",
                            "account_balance": 0,
                        },
                        {
                            "user_id": placed_bet.user_id,
                            "trans_amount": new_balance,
                            "trans_nature": "LBetWin",
                            "account_balance": new_balance,
                        },
                    ]
                    serializer = UserTransSerializer(data=data, many=True)
                    if serializer.is_valid():
                        serializer.save()
                    else:
                        raise Exception("Wrong Data From Recording Full Loan Payment")
                else:
                    # user still has debt or paid fully with 0 balance
                    data = {
                        "user_id": placed_bet.user_id,
                        "trans_amount": placed_bet.loan_amount,
                        "trans_nature": "LoanPayment",
                        "account_balance": new_balance,
                    }
                    serializer = UserTransSerializer(data=data)
                    if serializer.is_valid():
                        serializer.save()
                    else:
                        raise Exception("Wrong Data from Recording Partial Or Full Loan Payment")
        else:
            raise Exception("Wrong Data From Update Normal Bet")
    # lost the bet
    else:
        placed_bet.bet_outcome = "Lose"

    # saving changes made to placed bet
    placed_bet.save()
