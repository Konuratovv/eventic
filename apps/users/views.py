from rest_framework.generics import CreateAPIView
from apps.profiles.models import User
from apps.users.serializer import RegisterSerializer
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.views import TokenObtainPairView


class RegisterViewSet(CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]


class LoginViewSet(TokenObtainPairView):
    permission_classes = [AllowAny]
