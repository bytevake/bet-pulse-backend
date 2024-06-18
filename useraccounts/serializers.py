from rest_framework import serializers
from .models import UserTransactions


class UserTransSerializer(serializers.ModelSerializer): 
    class Meta:
        model = UserTransactions
        fields = ['user_id', 'trans_amount', 'trans_nature',
                  'account_balance',]