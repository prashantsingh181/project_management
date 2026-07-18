from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .views import UserCreateView, UserRetrieveView

urlpatterns = [
    path("register/", UserCreateView.as_view(), name="register"),
    path("me/", UserRetrieveView.as_view(), name="me"),
    path("token/", TokenObtainPairView.as_view(), name="token"),
    path("token/refresh/", TokenRefreshView.as_view(), name="refresh"),
]
