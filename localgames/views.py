from django.contrib.auth import authenticate, login
from decimal import Decimal
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from accounts.serializers import MessageSerializer
from betting_pulse.constants import LOAN_LOSE_IRT, LOAN_WIN_IRT
from useraccounts.models import UserAccounts
from useraccounts.serializers import UserTransSerializer
from useraccounts.loans import is_loan_eligible
from .models import Games
from .serializers import GamesSerializer, PlacedBetsSerializer

class GamesAPIView(APIView):
    """
    Handles All Operations For Local Games
    """
    def get(self, request, *args, **kwargs):
        """
        Used To Get All Games Added
        """
        games = Games.objects.all()
        serializer = GamesSerializer(games, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        """
        Used To Add Local Games to the Database
        """
        data = {
            'home': request.data.get('home'),
            'away': request.data.get('away'),
            'home_odds': request.data.get('home_odds'),
            'away_odds': request.data.get('away_odds'),
            'draw_odds': request.data.get('draw_odds'),
            'game_date': request.data.get('game_date'),
            'status': "Active",
        }
        serializer = GamesSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            message = {
                "message": "Successfully Added Local Games"
            }
            serializer = MessageSerializer(message)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class UpdateGameOutComeAPIView(APIView):
    """
    Will be Used To Update Game Outcomes
    """
    def post(self, request, *args, **kwargs):
        """
        Updates the outcome of a Game
        """
        game = Games.objects.get(id=request.data.get("game_id"))
        data = {
            "home": game.home,
            "away": game.away,
            "home_odds": game.home_odds,
            "away_odds": game.away_odds,
            "draw_odds": game.draw_odds,
            "game_date": game.game_date,
            "status": False,
            "outcome": request.data.get("outcome")
        }
        serializer = GamesSerializer(game, data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PlaceBetAPIView(APIView):
    """
    Will Handle Transactions Betting
    """
    def get(self, request, *args, **kwargs):
        """
        Will be used to get a users placed bets
        """
        pass

    def post(self, request, *args, **kwargs):
        """
        Will be Used To Place A Bet By a User
        """
        data = {
            'user_id': request.data.get("user_id"),
            'game_id': request.data.get("game_id"),
            'placed_bet': request.data.get("placed_bet"),
            'placed_amount': request.data.get("placed_amount"),
            'bet_outcome': "Pending",
        }

        # getting the possible win
        # TODO catch error incase of non existing game id
        game = Games.objects.get(id=data["game_id"])
        if data['placed_bet'] == 'Home':
            data['possible_win'] = round(data['placed_amount'] * game.home_odds, 2)
        elif data['placed_bet'] == 'Away':
            data['possible_win'] = round(data['placed_amount'] * game.away_odds, 2)
        elif data['placed_amount'] == 'Draw':
            data['possible_win'] = round(data['placed_amount'] * game.draw_odds, 2)
        else:
            # wrong placed bet
            message = {
                "message": "Wrong Placed Bet! Kindly Report Issue"
            }
            serializer = MessageSerializer(message)
            return Response(serializer.data, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = PlacedBetsSerializer(data=data)
        if serializer.is_valid():
            # get user account
            user_account = UserAccounts.objects.get(user_id=data['user_id'])

            if data['placed_amount'] > user_account.balance:
                amt_missing = data['placed_amount'] - user_account.balance

                if not is_loan_eligible(data['user_id'], amt_missing):
                    print("I am here")
                    message = {
                        "message": "Insufficient Balance",
                        }
                    serializer = MessageSerializer(message)
                    return Response(serializer.data, status=status.HTTP_400_BAD_REQUEST)
                
                rep_data = {
                    "loan_amount": amt_missing,
                    "winning_interest": LOAN_WIN_IRT,
                    "lossing_interest": LOAN_LOSE_IRT,
                    "debt_lose": amt_missing + (amt_missing * LOAN_LOSE_IRT),
                    "debt_win": amt_missing + (amt_missing * LOAN_WIN_IRT),
                }
                rep_data.update(data)
                return Response(rep_data, status=status.HTTP_402_PAYMENT_REQUIRED)
                
            # deduct placed amount from user
            new_balance = user_account.balance - data['placed_amount']

            # record the transaction
            data = {
                "user_id": user_account.user_id,
                "trans_amount": -data['placed_amount'],
                "trans_nature": "BetPlacement",
                "account_balance": new_balance
            }
            trans_serializer = UserTransSerializer(data=data)
            if trans_serializer.is_valid():
                trans_serializer.save()
                user_account.balance = new_balance
                user_account.save()
                # successful placement
                serializer.save()
                message = {
                    "message": "SuccessFully Placed Bet",
                    }
                serializer = MessageSerializer(message)
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response(trans_serializer.errors, status=status.HTTP_417_EXPECTATION_FAILED)
        return Response(serializer.errors, status=status.HTTP_417_EXPECTATION_FAILED)


class LoanPlaceBetsAPIView(APIView):
    """
    Used To Place Bets on Basis Of Loan
    """
    def post (self, request, *args, **kwargs):
        """
        Used To Complete Placed Bets On Loan
        """
        data = request.data # request data
        # passing loan amount to instance
        serializer = PlacedBetsSerializer(data=request.data,
            context={"loan_amount": request.data.get("loan_amount")})
        if serializer.is_valid():
            # get user account
            user_account = UserAccounts.objects.get(user_id=data['user_id'])

            # security checks
            if data['placed_amount'] < user_account.balance:
                message = {
                    "message": "Invalid Request",
                    }
                serializer = MessageSerializer(message)
                return Response(serializer.data, status=status.HTTP_400_BAD_REQUEST)
            
            if not is_loan_eligible(data['user_id'], data['loan_amount']):
                message = {
                    "message": "Invalid Request",
                    }
                serializer = MessageSerializer(message)
                return Response(serializer.data, status=status.HTTP_400_BAD_REQUEST)
                
            # deduct placed amount from user
            amount_to_deduct = round(Decimal(data['placed_amount']), 2)
            new_balance = user_account.balance - amount_to_deduct

            # record the transaction
            data = {
                "user_id": user_account.user_id,
                "trans_amount": -data['placed_amount'],
                "trans_nature": "LoanBetPlacement",
                "account_balance": new_balance
            }
            trans_serializer = UserTransSerializer(data=data)
            if trans_serializer.is_valid():
                trans_serializer.save()
                user_account.balance = new_balance
                user_account.save()
                # successful placement
                serializer.save()
                message = {
                    "message": "SuccessFully Placed Bet",
                    }
                serializer = MessageSerializer(message)
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response(trans_serializer.errors, status=status.HTTP_417_EXPECTATION_FAILED)
        return Response(serializer.errors, status=status.HTTP_417_EXPECTATION_FAILED)
