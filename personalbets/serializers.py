from rest_framework import serializers
from .models import PersonalBets


class PersonalBetsSerializer(serializers.ModelSerializer):
    class Meta:
        model = PersonalBets
        fields = ['__all__']
