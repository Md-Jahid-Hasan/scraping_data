from rest_framework import generics, permissions
from rest_framework_simplejwt.views import TokenObtainPairView

from .serializers import MyTokenObtainPairSerializer, UserCreateSerializer, UserDetailsSerializer


class LoginView(TokenObtainPairView):
    """Return access and refresh tokens for authorization."""
    serializer_class = MyTokenObtainPairSerializer


class CreateUserView(generics.CreateAPIView):
    """Create a new user in the system"""
    serializer_class = UserCreateSerializer


class CurrentUser(generics.RetrieveAPIView):
    """Return authenticated user."""
    serializer_class = UserDetailsSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user