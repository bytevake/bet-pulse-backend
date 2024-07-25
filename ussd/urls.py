from django.urls import path
from ussd.views import USSDCallBackURL


# Registering urls
urlpatterns = [
    path("", USSDCallBackURL.as_view()),
]
