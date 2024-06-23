from django.urls import path
from .views import DepositCashAPI, WithdrawCashAPI
from .views import UserTransAPIView

urlpatterns = [
    path("deposit/", DepositCashAPI.as_view(), name="depocash"),
    path("withdraw/", WithdrawCashAPI.as_view(), name="withdrawcash"),
    path("user-trans/<id>/", UserTransAPIView.as_view(), name="usertrans"),
]