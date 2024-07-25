from django.urls import path
from .views import RegisterUsersAPIView, LoginApIView
from .views import SearchUserAPiView

urlpatterns = [
    path("signup/", RegisterUsersAPIView.as_view(), name="signup"),
    path("login/", LoginApIView.as_view(), name="login"),
    path("search-users/<str:name>/", SearchUserAPiView.as_view(), name="login"),
]

