from rest_framework import status
from rest_framework.generics import CreateAPIView, UpdateAPIView
from apps.profiles.models import User
from apps.users.models import CustomUser
from apps.users.serializer import RegisterSerializer, CodeSerializer, SendCodeSerializer
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.response import Response
from apps.users.utils import send_verification_mail


class RegisterAPIView(CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        data = {"Status": "Success"}
        return Response(data, status=status.HTTP_200_OK)


class LoginViewSet(TokenObtainPairView):
    permission_classes = [AllowAny]


class SendCodeAPIView(UpdateAPIView):
    serializer_class = SendCodeSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        user = CustomUser.objects.get(id=self.request.user.id)
        return user

    def patch(self, request, *args, **kwargs):
        email = self.get_object().email
        send_verification_mail(email)
        return Response({'message': 'Verify code have sent successfully'})


class VerifyAPIView(UpdateAPIView):
    serializer_class = CodeSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        user = CustomUser.objects.get(id=self.request.user.id)
        return user

    def patch(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = self.get_object()
            code = serializer.validated_data['code']
            if user.code == code:
                user.is_verified = True
                user.save()
                return Response({'status': 'success'})
            return Response({'status': 'error'})

        return Response({'message': 'Serializer is not valid'})
