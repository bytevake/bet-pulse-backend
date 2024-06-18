from django.urls import path
from .views import DepositCashAPI, WithdrawCashAPI

urlpatterns = [
    path("deposit/", DepositCashAPI.as_view(), name="depocash"),
    path("withdraw/", WithdrawCashAPI.as_view(), name="withdrawcash"),
]