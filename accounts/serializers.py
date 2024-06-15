from rest_framework import serializers
from .models import CustomUser


class AccountSerializer(serializers.ModelSerializer): 
    class Meta:
        model = CustomUser
        fields = ['id', 'password', 'last_login', 'username', 'first_name',
                  'last_name', 'date_joined', 'email', 'phone_no',
                  'national_id'
                  ]
        
        extra_kwargs = {
            "password": {"write_only": True}
        }

    def create(self, validated_data):
        """
        Creates a new user profile from the request's data
        """
        account = CustomUser(**validated_data)
        account.set_password(account.password)
        account.save()
        return account

class MessageSerializer(serializers.Serializer):
    """
    Serializes Sent Responses
    """
    message = serializers.CharField(max_length=100)