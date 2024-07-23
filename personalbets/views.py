from django.db import transaction
from decimal import Decimal
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from accounts.serializers import MessageSerializer
from betting_pulse.constants import PERSONAL_BET_RATE, WITNESS_BET_RATE
from useraccounts.models import UserAccounts
from useraccounts.serializers import UserTransSerializer
from .models import WitnessPersonalBets, AgainstPersonalBets, BetterPersonalBets
from .models import PersonalBets
from .serializers import PersonalBetsSerializer


# Create your views here.
class PersonalBetAPIView(APIView):
    """
    Will Handle Placement of the Personal Bet
    """
    def post(self, request, *args, **kwargs):
        """
        Handles Placement of the first bet
        """
        against_id = request.data.get("against")
        witness_id = request.data.get("witness")
        better_id = request.data.get("better")
        if against_id is None or witness_id is None or better_id is None:
            message = {"message": "Missing better or against or witness"}
            serializer = MessageSerializer(message)
            return Response(serializer.data, status=status.HTTP_400_BAD_REQUEST)
        witness = UserAccounts.objects.filter(user_id=witness_id)
        if not witness:
            message = {"message": "Witness Doesn't Exist"}
            serializer = MessageSerializer(message)
            return Response(serializer.data, status=status.HTTP_400_BAD_REQUEST)
        against = UserAccounts.objects.filter(user_id=against_id)
        if not against:
            message = {"message": "Against Better Doesn't Exist"}
            serializer = MessageSerializer(message)
            return Response(serializer.data, status=status.HTTP_400_BAD_REQUEST)
        better = UserAccounts.objects.filter(user_id=better_id)
        if not better:
            message = {"message": "Better Doesn't Exist"}
            serializer = MessageSerializer(message)
            return Response(serializer.data, status=status.HTTP_400_BAD_REQUEST)
        description = request.data.get("description")
        if not description:
            message = {"message": "Description Is Required"}
            serializer = MessageSerializer(message)
            return Response(serializer.data, status=status.HTTP_400_BAD_REQUEST)
        end_time = request.data.get("end_time")
        if not end_time:
            message = {"message": "End Time Is Required"}
            serializer = MessageSerializer(message)
            return Response(serializer.data, status=status.HTTP_400_BAD_REQUEST)
        amount_placed = request.data.get("amount_placed")
        # changing value to decimal
        amount_placed = round(Decimal(amount_placed), 2)
        # checking account balance
        if amount_placed > better[0].balance:
            # return message saying insufficient balance
            message = {"message": "Insufficient Balance"}
            serializer = MessageSerializer(message)
            return Response(serializer.data, status=status.HTTP_400_BAD_REQUEST)
        
        # calculations of amount
        witness_amount = amount_placed * WITNESS_BET_RATE
        trans_amount = amount_placed * PERSONAL_BET_RATE
        posiible_win = (amount_placed * 2) - (trans_amount * 2) - witness_amount

        # transactions
        with transaction.atomic():
            data = {
                "trans_amount": (trans_amount * 2),
                "possible_win": posiible_win,
                "amount_placed": (amount_placed * 2),
                "witness_amount": witness_amount,
                "better_confirm": True,
                "description": description,
                "end_time": end_time,
            }
            serializer = PersonalBetsSerializer(data=data)
            if serializer.is_valid():
                serializer.save()
            else:
                raise Exception("Wrong Data From Serializer")
            # create bet against
            against = AgainstPersonalBets.objects.create(bet_id=serializer.instance, 
                against=against, amount_placed=amount_placed, trans_amount=trans_amount)
            # create bet initiater
            better = BetterPersonalBets.objects.create(better=better, better_confirm=True,
                trans_amount=trans_amount, amount_placed=amount_placed,
                bet_id=serializer.instance)
            # create witness
            witness = WitnessPersonalBets.objects.create(bet_id=serializer.instance,
                witness=witness, amount=witness_amount)
            # deductions users cash
            better.better.balance -= amount_placed
            better.save()
            
            # record transaction
            trans_data = {
                'user_id': better,
                'trans_amount': -trans_amount,
                'trans_nature': "PersonalBet",
                'account_balance': better.better.balance
            }
            trans_serializer = UserTransSerializer(data=trans_data)
            if trans_serializer.is_valid():
                trans_serializer.save()
            else:
                raise Exception("Wrong Data From Trans Serializer")
        message = {"message": "Personal Bet Successfully Placed"}
        serializer = MessageSerializer(message)
        return Response(serializer.data, status=status.HTTP_200_OK)


class AgainstConfrimAPIView(APIView):
    """
    WIll Handle Confirmation from the against better
    """
    def post(self, request, *args, **kwargs):
        """
        Handles connfirmation of the against better
        """
        bet_id = request.data.get("bet_id")
        against_beter = request.data.get("against")
        confirmation = request.data.get("confirmation")
        if not bet_id or not confirmation or not against_beter:
            message = {
                "message": "Bet ID or Confirmation or Against Better is Required"
                }
            serializer = MessageSerializer(message)
            return Response(serializer.data, status=status.HTTP_400_BAD_REQUEST)

        personal_bet = PersonalBets.objects.filter(id=bet_id)
        if personal_bet[0].outcome == "cancelled":
            message = {"message": "Bet Has Been Cancelled"}
            serializer = MessageSerializer(message)
            return Response(serializer.data, status=status.HTTP_200_OK)
        against_beter = AgainstPersonalBets.objects.filter(against=against_beter,
            bet_id=personal_bet)
        if  confirmation:
            # check balance
            if against_beter[0].amount_placed > against_beter[0].against.balance:
                message = {
                    "message": "Insufficient Funds To Confirm Bet"
                }
                serializer = MessageSerializer(message)
                return Response(serializer.data, status=status.HTTP_200_OK)
            with transaction.atomic():
                against_beter[0].confirmation = True
                # check whether witness has made confirmed
                witness_dec = WitnessPersonalBets.objects.get(bet_id=personal_bet[0]).confirmation
                if witness_dec:
                    # set status to confirmed
                    personal_bet[0].outcome = "confirmed"
                # subtract the placed cash
                against_beter[0].confirmation = True
                against_beter[0].against.balance -= against_beter[0].amount_placed
                against_beter[0].against.save()
                against_beter[0].save()
                personal_bet[0].save()
                # record transaction
                trans_data = {
                    'user_id': against_beter[0],
                    'trans_amount': -against_beter[0].amount_placed,
                    'trans_nature': "PersonalBet",
                    'account_balance': against_beter[0].against.balance
                }
                trans_serializer = UserTransSerializer(data=trans_data)
                if trans_serializer.is_valid():
                    trans_serializer.save()
                else:
                    raise Exception("Wrond Data From Trans Serializer")
            message = {
                "message": "Successfully Accepted Bet"
            }
            serializer = MessageSerializer(message)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            # return personal better cash subtract bet rate
            with transaction.atomic():
                against_beter[0].confirmation = False
                personal_bet[0].outcome = "cancelled"
                against_beter[0].save()
                personal_bet[0].save()
                
                # get intial better
                intial_better = BetterPersonalBets.objects.get(bet_id=personal_bet[0])
                trans_data = [
                    {
                        'user_id': intial_better,
                        'trans_amount': intial_better.amount_placed,
                        'trans_nature': "PersonalBetReturns",
                        'account_balance': intial_better.better.balance
                    },
                    {
                        'user_id': intial_better,
                        'trans_amount': intial_better.trans_amount,
                        'trans_nature': "PersonalBetRate",
                        'account_balance': intial_better.better.balance
                    },
                ]
                trans_serializer = UserTransSerializer(data=trans_data, many=True)
                if trans_serializer.is_valid():
                    trans_serializer.save()
                else:
                    raise Exception("Wrong Data From Trans Serializer")
                intial_better.better.balance += (intial_better.amount_placed - intial_better.trans_amount)
                intial_better.better.save()
            message = {
                "message": "Successsfuly Declined Bet"
            }
            serializer = MessageSerializer(message)
            return Response(serializer.data, status=status.HTTP_200_OK)
            

class WitnessConfrimAPIView(APIView):
    """"
    Will Handle Confrimation of PersonalBet from Witness
    """
    def post(sellf, request, *args, **kwargs):
        """
        Handles Witness Confrimation
        """
        bet_id = request.data.get("bet_id")
        witness = request.data.get("witness")
        confirmation = request.data.get("confirmation")
        if not bet_id or not confirmation or not witness:
            message = {
                "message": "Bet ID or Confirmation or Witness is Required"
                }
            serializer = MessageSerializer(message)
            return Response(serializer.data, status=status.HTTP_400_BAD_REQUEST)
        
        personal_bet = PersonalBets.objects.filter(id=bet_id)
        if personal_bet[0].outcome == "cancelled":
            message = {"message": "Bet Has Been Cancelled"}
            serializer = MessageSerializer(message)
            return Response(serializer.data, status=status.HTTP_200_OK)
        witness = WitnessPersonalBets.objects.get(bet_id=personal_bet)
        against_dec = AgainstPersonalBets.objects.get(bet_id=personal_bet)
        if confirmation:
            if against_dec.confirmation:
                personal_bet[0].outcome = "confirmed"
            with transaction.atomic():
                personal_bet[0].save()
                witness.confirmation = True
                witness.save()
            message = {
                "message": "Succesfully Confrimed bet"
            }
            serializer = MessageSerializer(message)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            # refund those who have confirmed their cash and record transactions
            with transaction.atomic():
                witness.confirmation = False
                personal_bet[0].outcome = "cancelled"
                if against_dec.confirmation:
                    trans_data = [
                        {
                            'user_id': against_dec,
                            'trans_amount': against_dec.amount_placed,
                            'trans_nature': "PersonalBetReturns",
                            'account_balance': against_dec.against.balance
                        },
                        {
                            'user_id': against_dec,
                            'trans_amount': against_dec.trans_amount,
                            'trans_nature': "PersonalBetRate",
                            'account_balance': against_dec.against.balance
                        },
                    ]
                    trans_serializer = UserTransSerializer(data=trans_data, many=True)
                    if trans_serializer.is_valid():
                        trans_serializer.save()
                    else:
                        raise Exception("Wrong Data From Trans Serializer")
                    against_dec.against.balance += (against_dec.amount_placed -
                        against_dec.trans_amount)
                    against_dec.against.save()

                int_beter = BetterPersonalBets.objects.get(bet_id=personal_bet[0])
                if int_beter.better_confirm:
                    trans_data = [
                        {
                            'user_id': int_beter,
                            'trans_amount': int_beter.amount_placed,
                            'trans_nature': "PersonalBetReturns",
                            'account_balance': int_beter.better.balance
                        },
                        {
                            'user_id': int_beter,
                            'trans_amount': int_beter.trans_amount,
                            'trans_nature': "PersonalBetRate",
                            'account_balance': int_beter.better.balance
                        },
                    ]
                    trans_serializer = UserTransSerializer(data=trans_data, many=True)
                    if trans_serializer.is_valid():
                        trans_serializer.save()
                    else:
                        raise Exception("Wrong Data From Trans Serializer")
                    int_beter.better.balance += (int_beter.amount_placed -
                        int_beter.trans_amount)
                    int_beter.better.save()
                witness.save()
                personal_bet[0].save()
            message = {
                "message": "Succesfully Declined bet"
            }
            serializer = MessageSerializer(message)
            return Response(serializer.data, status=status.HTTP_200_OK)