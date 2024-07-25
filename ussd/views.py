from django.shortcuts import render
from rest_framework.status import HTTP_200_OK
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response

# Create your views here.


class USSDCallBackURL(GenericAPIView):
    def post(self, request, *args, **kwargs):
        session_id = request.data.get("sessionId", None)
        phone_number = request.data.get("phoneNumber", None)
        text = request.data.get("text", "default")

        if text == "":
            response = "CON What would you want to check from Erick \n"
            response += "1. My Account \n"
            response += "2. My phone number"

        elif text == "1":
            response = "CON Choose account information you want to view \n"
            response += "1. Account number \n"
            response += "2. Account balance"

        elif text == "1*1":
            accountNumber = "ACC1001"
            response = "END Your account number is " + accountNumber

        elif text == "1*2":
            balance = "KES 10,000"
            response = "END Your balance is " + balance

        elif text == "2":
            response = "END This is your phone number " + phone_number

        return Response(
            text,
            status=HTTP_200_OK,
        )
