from rest_framework import generics
from rest_framework.permissions import AllowAny, IsAuthenticated

from .serializers import UserRegisterSerializer, UserSerializer

# Create your views here.


class RegisterView(generics.CreateAPIView):
    serializer_class = UserRegisterSerializer
    permission_classes = [AllowAny]


class MeView(generics.RetrieveAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user
