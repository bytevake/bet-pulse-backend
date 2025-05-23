"""
Has Reusable Methods
"""
from .models import PlacedBets
from useraccounts.serializers import UserTransSerializer
from useraccounts.models import UserAccounts
from betting_pulse.constants import LOAN_LOSE_IRT, LOAN_WIN_IRT

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

def update_loan_bet(placed_bet: PlacedBets, outcome: str):
    """
    Used to bets that are on looan
    Args:
        placed_bet(PlacedBet): The Placed bet instance
        outcome: The outcome of the game
    Return:
        None
    """
    user_acc = UserAccounts.objects.get(user_id=placed_bet.user_id)
    prev_balance = placed_bet.user_id.balance
    # won the bet
    if placed_bet.placed_bet == outcome:
        placed_bet.bet_outcome = "Win"
        loan_irt = placed_bet.loan_amount * LOAN_WIN_IRT
        new_balance = (placed_bet.possible_win - loan_irt) + prev_balance
        # update placed loan irt and total loan
        placed_bet.loan_irt = loan_irt
        placed_bet.total_loan = loan_irt + placed_bet.loan_amount
        # record pay loan irt
        data = {
            "user_id": placed_bet.user_id,
            "trans_amount": -loan_irt,
            "trans_nature": "PIL",
            "account_balance": new_balance,
        }
        serializer = UserTransSerializer(data=data)
        if serializer.is_valid():
            serializer.save()

            if prev_balance < 0:
                # user has loan
                if new_balance < 0:
                    # loan not fully paid
                    data = [
                        # record bet win
                        {
                            "user_id": placed_bet.user_id,
                            "trans_amount": placed_bet.possible_win,
                            "trans_nature": "BetWin",
                            "account_balance": new_balance
                        },
                        # record loan payment
                        {
                            "user_id": placed_bet.user_id,
                            "trans_amount": (placed_bet.possible_win - loan_irt),
                            "trans_nature": "LoanPayment",
                            "account_balance": new_balance,
                        },
                    ]
                    serializer = UserTransSerializer(data=data, many=True)
                    if serializer.is_valid():
                        serializer.save()
                        # update account balance
                        user_acc.balance = new_balance
                        user_acc.save()
                         
                    else:
                        raise Exception("Wrong Data From Not Full Loan Pay Win")
                else:
                    # loan fully paid
                    data = [
                        # record bet win
                        {
                            "user_id": placed_bet.user_id,
                            "trans_amount": placed_bet.possible_win,
                            "trans_nature": "BetWin",
                            "account_balance": new_balance
                        },
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
                        # update users data
                        user_acc.balance = new_balance
                        user_acc.save()
                    else:
                        raise Exception("Wrong Data From Pay Full Loan Win Bet")
            else:
                # user doesn't have loan
                data = {
                    "user_id": placed_bet.user_id,
                    "trans_amount": placed_bet.possible_win,
                    "trans_nature": "BetWin",
                    "account_balance": new_balance,
                }
                serializer = UserTransSerializer(data=data)
                if serializer.is_valid():
                    serializer.save()
                    # update users account
                    user_acc.balance = new_balance
                    user_acc.save()
                else:
                    raise Exception("Wrong Data From Loan Bet Win")       
        else:
            raise Exception("Wrong Data From Paying Loan Win IRT On Loan Bet")

    # lost the bet
    else:
        placed_bet.bet_outcome = "Lose"
        loan_irt = placed_bet.loan_amount * LOAN_LOSE_IRT
        new_balance = prev_balance - loan_irt

        # record pay loan irt
        data = {
            "user_id": placed_bet.user_id,
            "trans_amount": -loan_irt,
            "trans_nature": "PIL",
            "account_balance": new_balance,
        }
        serializer = UserTransSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            # update users account
            user_acc.balance = new_balance
            user_acc.save()
            # update placed loan irt and total loan
            placed_bet.loan_irt = loan_irt
            placed_bet.total_loan = loan_irt + placed_bet.loan_amount
        else:
            raise Exception("Wrong Data From Paying Loan Lose IRT On Loan Bet")
    
    # save changes made placed bet instance
    placed_bet.save()