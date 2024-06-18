from django.contrib.auth import authenticate, login
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from .models import CustomUser
from .serializers import AccountSerializer, MessageSerializer


class LoginApIView(APIView):
    """
    handles User activities such as Login and Logout
    """
    def get(self, request, *args, **kwargs):
        """
        Handles loging out of the user
        """
        pass

    def post(self, request, *args, **kwargs):
        """
        Handles log in of the user
        """
        
        username = request.data.get("username")
        password = request.data.get("password")
        user = authenticate(username=username, password=password)

        # if user exists
        if user:
            serializer = AccountSerializer(user)
            login(request, user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        # user doesn't exist
        else:
            message = {
                "message": "Invalid User Credentials",
                }
            serializer = MessageSerializer(message)
            return Response(serializer.data, status=status.HTTP_403_FORBIDDEN)

class RegisterUsersAPIView(APIView):
    """
    Handles Registatration of Users
    """
    def post(self, request, *args, **kwargs):
        """
        Handles registration of Users
        """
        data = {
            "username": request.data.get("username"),
            "first_name": request.data.get("first_name"),
            "last_name": request.data.get("last_name"),
            "email": request.data.get("email"),
            "password": request.data.get("password"),
            "phone_no": request.data.get("phone_no"),
            "national_id": request.data.get("national_id")
        }

        serializer = AccountSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

