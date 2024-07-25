from django.db import transaction
from decimal import Decimal
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from accounts.serializers import MessageSerializer
from betting_pulse.constants import PERSONAL_BET_RATE, WITNESS_BET_RATE
from sendmail.sendmail import SendMail
from useraccounts.models import UserAccounts
from useraccounts.serializers import UserTransSerializer
from .models import WitnessPersonalBets, AgainstPersonalBets, BetterPersonalBets
from .models import PersonalBets
from .serializers import PersonalBetsSerializer
import json


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
        posiible_win = (amount_placed * 2) - (trans_amount * 2) - (witness_amount * 2)

        # transactions
        with transaction.atomic():
            data = {
                "trans_amount": round((trans_amount * 2), 2),
                "posiible_win": round(posiible_win, 2),
                "amount_placed": (amount_placed * 2),
                "witness_amount": round(witness_amount, 2),
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
                against=against[0], amount_placed=amount_placed, trans_amount=trans_amount)
            # create bet initiater
            better = BetterPersonalBets.objects.create(better=better[0], better_confirm=True,
                trans_amount=trans_amount, amount_placed=amount_placed,
                bet_id=serializer.instance)
            # create witness
            witness = WitnessPersonalBets.objects.create(bet_id=serializer.instance,
                witness=witness[0], amount=witness_amount)
            # deductions users cash
            better.better.balance -= amount_placed
            better.better.save()
            
            # record transaction
            trans_data = {
                'user_id': better.better,
                'trans_amount': -round(trans_amount, 2),
                'trans_nature': "PersonalBet",
                'account_balance': better.better.balance
            }
            trans_serializer = UserTransSerializer(data=trans_data)
            if trans_serializer.is_valid():
                trans_serializer.save()
            else:
                raise Exception("Wrong Data From Trans Serializer")
        # sending to better
        sms_message = f"Your Personal Bet of description:{description}/n has been sent to {against.against.user_id.username} and witness {witness.witness.user_id.username}" 
        sender_instance = SendMail(username="", api_key="", sender="")
        sender_instance.send(message=sms_message, recipients=[f"{better.better.user_id.phone_no}"])
        # sending to against
        sms_message = f"{against.against.user_id.username} has a personal bet against you and the chosen witness is {witness.witness.user_id.username}, visit app for more details" 
        sender_instance = SendMail(username="", api_key="", sender="")
        sender_instance.send(message=sms_message, recipients=[f"{against.against.user_id.phone_no}"])
        # sending to witness
        sms_message = f"{against.against.user_id.username} has chosen you as a witness in a personal bet, visit app for more info" 
        sender_instance = SendMail(username="", api_key="", sender="")
        sender_instance.send(message=sms_message, recipients=[f"{witness.witness.user_id.phone_no}"])
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
        if not bet_id or (confirmation is None) or not against_beter:
            message = {
                "message": "Bet ID or Confirmation or Against Better is Required"
                }
            serializer = MessageSerializer(message)
            return Response(serializer.data, status=status.HTTP_400_BAD_REQUEST)

        personal_bet = PersonalBets.objects.get(id=bet_id)
        if personal_bet.outcome == "cancelled":
            message = {"message": "Bet Has Been Cancelled"}
            serializer = MessageSerializer(message)
            return Response(serializer.data, status=status.HTTP_200_OK)
        against_beter = AgainstPersonalBets.objects.get(bet_id=personal_bet)
        witness = WitnessPersonalBets.objects.get(bet_id=personal_bet)
        if  confirmation:
            # check balance
            if against_beter.amount_placed > against_beter.against.balance:
                message = {
                    "message": "Insufficient Funds To Confirm Bet"
                }
                serializer = MessageSerializer(message)
                return Response(serializer.data, status=status.HTTP_200_OK)
            with transaction.atomic():
                against_beter.confirmation = True
                # check whether witness has made confirmed
                witness_dec = WitnessPersonalBets.objects.get(bet_id=personal_bet).confirmation
                if witness_dec:
                    # set status to confirmed
                    personal_bet.outcome = "confirmed"
                # subtract the placed cash
                against_beter.confirmation = True
                against_beter.against.balance -= against_beter.amount_placed
                against_beter.against.save()
                against_beter.save()
                personal_bet.save()
                # record transaction
                trans_data = {
                    'user_id': against_beter.against,
                    'trans_amount': -round(against_beter.amount_placed, 2),
                    'trans_nature': "PersonalBet",
                    'account_balance': against_beter.against.balance
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
                against_beter.confirmation = False
                personal_bet[0].outcome = "cancelled"
                against_beter.save()
                personal_bet[0].save()
                
                # get intial better
                intial_better = BetterPersonalBets.objects.get(bet_id=personal_bet[0])
                trans_data = [
                    {
                        'user_id': intial_better.better,
                        'trans_amount': round(intial_better.amount_placed, 2),
                        'trans_nature': "PersonalBetReturns",
                        'account_balance': intial_better.better.balance
                    },
                    {
                        'user_id': intial_better.better,
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
            # sending to against
            sms_message = f"You have successfully cancelled personal bet by {intial_better.better.user_id.username} with description {personal_bet.description}" 
            sender_instance = SendMail(username="", api_key="", sender="")
            sender_instance.send(message=sms_message, recipients=[f"{against_beter.against.user_id.phone_no}"])
            # sending to witness
            sms_message = f"The Personal bet from {intial_better.better.user_id.username} that you are a witness with description {personal_bet.description} has been cancelled by {against_beter.against.user_id.username}" 
            sender_instance = SendMail(username="", api_key="", sender="")
            sender_instance.send(message=sms_message, recipients=[f"{witness.witness.user_id.phone_no}"])
            # sending to better
            sms_message = f"Your Personal bet with description {personal_bet.description} has been cancelled by {against_beter.against.user_id.username}" 
            sender_instance = SendMail(username="", api_key="", sender="")
            sender_instance.send(message=sms_message, recipients=[f"{intial_better.better.user_id.phone_no}"])
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
        if not bet_id or (confirmation is None) or not witness:
            message = {
                "message": "Bet ID or Confirmation or Witness is Required"
                }
            serializer = MessageSerializer(message)
            return Response(serializer.data, status=status.HTTP_400_BAD_REQUEST)
        
        personal_bet = PersonalBets.objects.get(id=bet_id)
        print(personal_bet)
        if personal_bet.outcome == "cancelled":
            message = {"message": "Bet Has Been Cancelled"}
            serializer = MessageSerializer(message)
            return Response(serializer.data, status=status.HTTP_200_OK)
        witness = WitnessPersonalBets.objects.get(bet_id=personal_bet)
        against_dec = AgainstPersonalBets.objects.get(bet_id=personal_bet)
        if confirmation:
            if against_dec.confirmation:
                personal_bet.outcome = "confirmed"
            with transaction.atomic():
                personal_bet.save()
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
                personal_bet.outcome = "cancelled"
                print(personal_bet.outcome)
                personal_bet.save()
                print(personal_bet.outcome)
                if against_dec.confirmation:
                    trans_data = [
                        {
                            'user_id': against_dec.against,
                            'trans_amount': against_dec.amount_placed,
                            'trans_nature': "PersonalBetReturns",
                            'account_balance': against_dec.against.balance
                        },
                        {
                            'user_id': against_dec.against,
                            'trans_amount': against_dec.trans_amount,
                            'trans_nature': "PersonalBetRate",
                            'account_balance': against_dec.against.balance
                        },
                    ]
                    trans_serializer = UserTransSerializer(data=trans_data, many=True)
                    if trans_serializer.is_valid():
                        trans_serializer.save()
                    else:
                        print(trans_serializer.errors)
                        raise Exception("Wrong Data From Trans Serializer")
                    against_dec.against.balance += (against_dec.amount_placed -
                        against_dec.trans_amount)
                    against_dec.against.save()

                int_beter = BetterPersonalBets.objects.get(bet_id=personal_bet)
                if int_beter.better_confirm:
                    trans_data = [
                        {
                            'user_id': int_beter.better,
                            'trans_amount': int_beter.amount_placed,
                            'trans_nature': "PersonalBetReturns",
                            'account_balance': int_beter.better.balance
                        },
                        {
                            'user_id': int_beter.better,
                            'trans_amount': int_beter.trans_amount,
                            'trans_nature': "PersonalBetRate",
                            'account_balance': int_beter.better.balance
                        },
                    ]
                    trans_serializer = UserTransSerializer(data=trans_data, many=True)
                    if trans_serializer.is_valid():
                        trans_serializer.save()
                    else:
                        print(trans_serializer.errors)
                        raise Exception("Wrong Data From Trans Serializer")
                    int_beter.better.balance += (int_beter.amount_placed -
                        int_beter.trans_amount)
                    int_beter.better.save()
                witness.save()
            # sending to witness
            sms_message = f"You have successfully cancelled personal bet by {int_beter.better.user_id.username} with description {personal_bet.description}" 
            sender_instance = SendMail(username="", api_key="", sender="")
            sender_instance.send(message=sms_message, recipients=[f"{witness.witness.user_id.phone_no}"])
            # sending to against
            sms_message = f"The Personal bet from {int_beter.better.user_id.username} that was against you with description {personal_bet.description} has been cancelled by {witness.witness.user_id.username}" 
            sender_instance = SendMail(username="", api_key="", sender="")
            sender_instance.send(message=sms_message, recipients=[f"{against_dec.against.user_id.phone_no}"])
            # sending to better
            sms_message = f"Your Personal bet with description {personal_bet.description} has been cancelled by {witness.witness.user_id.username}" 
            sender_instance = SendMail(username="", api_key="", sender="")
            sender_instance.send(message=sms_message, recipients=[f"{int_beter.better.user_id.phone_no}"])
            message = {
                "message": "Succesfully Declined bet"
            }
            serializer = MessageSerializer(message)
            return Response(serializer.data, status=status.HTTP_200_OK)

class GetPersonalAPIView(APIView):
    """
    Returns Uncancelled and Unconfrimed Personal Data
    """
    def get(self, request, *args, **kwargs):
        """
        Returns Uncancelled and Unconfrimed Personal Data
        """
        user_id = kwargs["user_id"]
        againsts_bets = AgainstPersonalBets.objects.filter(against=user_id, confirmation=False)
        beter_bets = BetterPersonalBets.objects.filter(better=user_id, better_confirm=False)
        witness_bets = WitnessPersonalBets.objects.filter(witness=user_id, confirmation=False)

        response_data = []

        for against in againsts_bets:
            if against.bet_id.outcome != "confirmed" or against.bet_id.outcome != "cancelled":
                not_data = {
                    "bet_id": against.bet_id.id,
                    "amount_placed": against.bet_id.amount_placed,
                    "posiible_win": against.bet_id.posiible_win,
                    "witness_amount": against.bet_id.witness_amount,
                    "trans_amount": against.trans_amount /2,
                    "end_time": against.bet_id.end_time,
                    "description": against.bet_id.description,
                    "type": "against",
                }
                response_data.append(not_data)

        for beter in beter_bets:
            if beter.bet_id.outcome != "confirmed" or beter.bet_id.outcome != "cancelled":
                not_data = {
                    "bet_id": beter.bet_id.id,
                    "amount_placed": beter.bet_id.amount_placed,
                    "posiible_win": beter.bet_id.posiible_win,
                    "witness_amount": beter.bet_id.witness_amount,
                    "trans_amount": beter.trans_amount /2,
                    "end_time": beter.bet_id.end_time,
                    "description": beter.bet_id.description,
                    "type": "beter",
                    }
                response_data.append(not_data)
        
        for witness in witness_bets:
            if witness.bet_id.outcome != "confirmed" or witness.bet_id.outcome != "cancelled":
                not_data = {
                    "bet_id": witness.bet_id.id,
                    "amount_placed": witness.bet_id.amount_placed,
                    "posiible_win": witness.bet_id.posiible_win,
                    "witness_amount": witness.bet_id.witness_amount,
                    "trans_amount": witness.bet_id.trans_amount /2,
                    "end_time": witness.bet_id.end_time,
                    "description": witness.bet_id.description,
                    "type": "witness",
                }
            response_data.append(not_data)
        return Response(response_data ,status=status.HTTP_200_OK)