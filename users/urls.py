from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .views import UserCreateView, UserRetrieveView

urlpatterns = [
    path("register/", UserCreateView.as_view()),
    path("me/", UserRetrieveView.as_view()),
    path("token/", TokenObtainPairView.as_view()),
    path("token/refresh/", TokenRefreshView.as_view()),
]
