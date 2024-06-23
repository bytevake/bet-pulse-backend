from django.contrib.auth import authenticate, login
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from accounts.models import CustomUser
from accounts.serializers import MessageSerializer
from useraccounts.models import UserAccounts
from .models import UserTransactions
from .serializers import UserTransSerializer

# TODO change to use user id
class DepositCashAPI(APIView):
    """
    Deposits Money
    """
    def post(self, request, *args, **kwargs):
        """
        Used to handle deposition of money to a
        Users Account
        """
        phone_no = request.data.get("phone_no")
        amount = request.data.get("amount")
        # TODO  catch exception for an non existing user
        user = CustomUser.objects.get(phone_no=phone_no, is_staff=False)

        # get user account
        user_account = UserAccounts.objects.get(user_id=user)
        new_balance = user_account.balance + amount

        # record the transaction
        data = {
            "user_id": user_account.user_id,
            "trans_amount": amount,
            "trans_nature": "Deposit",
            "account_balance": new_balance
        }
        serializer = UserTransSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            user_account.balance = new_balance
            user_account.save()
            data = {
                "message": "SuccessFully Deposited",
                }
            serializer = MessageSerializer(data)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_417_EXPECTATION_FAILED)

class WithdrawCashAPI(APIView):
    """
    Used to handle A user withdrawing of a users
    money
    """
    def post(self, request, *args, **kwargs):
        """
        Used to handle deposition of money to a
        Users Account
        """
        phone_no = request.data.get("phone_no")
        amount = request.data.get("amount")
        # TODO  catch exception for an non existing user
        user = CustomUser.objects.get(phone_no=phone_no, is_staff=False)

        # get user account
        user_account = UserAccounts.objects.get(user_id=user)
        if amount > user_account.balance:
            data = {
                "message": "Insufficient Balance",
                }
            serializer = MessageSerializer(data)
            return Response(serializer.data, status=status.HTTP_400_BAD_REQUEST)
        new_balance = user_account.balance - amount

        # record the transaction
        data = {
            "user_id": user_account.user_id,
            "trans_amount": -amount,
            "trans_nature": "Withdrawal",
            "account_balance": new_balance
        }
        serializer = UserTransSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            user_account.balance = new_balance
            user_account.save()
            data = {
                "message": "SuccessFully Withdrawn",
                }
            serializer = MessageSerializer(data)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_417_EXPECTATION_FAILED)

class UserTransAPIView(APIView):
    """
    Will be used to get a users transactions
    """
    # TODO add security features, restricting not getting a users data
    def get(self, request, *args, **kwargs):
        """
        Returns a single users transaction
        """
        trans = UserTransactions.objects.filter(user_id=kwargs.get("id"))
        serializer = UserTransSerializer(trans, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)