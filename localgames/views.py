from django.contrib.auth import authenticate, login
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from accounts.serializers import MessageSerializer
from .models import Games
from .serializers import GamesSerializer

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
