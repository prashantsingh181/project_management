from rest_framework import generics, permissions

from .models import User
from .serializers import MeSerializer, RegisterSerializer


class UserCreateView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = (permissions.AllowAny,)


class UserRetrieveView(generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = MeSerializer

    def get_object(self):
        return self.request.user
