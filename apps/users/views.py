from datetime import timedelta

from django.contrib.auth.hashers import make_password
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import status
from rest_framework.mixins import UpdateModelMixin
from rest_framework_simplejwt.tokens import AccessToken
from django.utils.crypto import constant_time_compare
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView

from rest_framework.generics import CreateAPIView, GenericAPIView
from apps.profiles.models import User
from apps.users.models import CustomUser
from apps.profiles.serializer import SendResetCodeSerializer, ChangePasswordSerializer
from apps.users.serializer import RegisterSerializer, CodeSerializer, SendCodeSerializer
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


class SendEmailCodeAPIView(UpdateModelMixin, GenericAPIView):
    serializer_class = SendCodeSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        user = CustomUser.objects.get(id=self.request.user.id)
        return user

    def patch(self):
        email = self.get_object().email
        send_verification_mail(email)
        return Response({'status': 'success'})


class VerifyEmailAPIView(UpdateModelMixin, GenericAPIView):
    serializer_class = CodeSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        user = CustomUser.objects.get(id=self.request.user.id)
        return user

    def patch(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = self.get_object()
            code = serializer.validated_data['code']
            if user.code == code:
                user.is_verified = True
                user.code = None
                user.save()
                return Response({'status': 'success'})
            return Response({'status': 'error'})

        return Response({'message': 'Serializer is not valid'})


class SendResetAPiView(UpdateModelMixin, GenericAPIView):
    serializer_class = SendResetCodeSerializer

    def get_object(self):
        user = CustomUser.objects.get(email=self.request.data.get('email'))
        return user

    def patch(self):
        try:
            email = self.get_object().email
        except ObjectDoesNotExist:
            return Response({'status': 'error'}, status=status.HTTP_400_BAD_REQUEST)
        send_verification_mail(email)
        return Response({'status': 'success'}, status=status.HTTP_200_OK)


class CheckResetCodeAPIView(UpdateModelMixin, GenericAPIView):
    serializer_class = CodeSerializer

    def patch(self):
        code = self.request.data.get('code')
        email = self.request.data.get('email')
        try:
            user = CustomUser.objects.get(email=email)
            if user.code == code:
                user.code = None
                user.save()
        except ObjectDoesNotExist:
            return Response({'status': 'error'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            access_token = AccessToken.for_user(user)
            access_token.set_exp(lifetime=timedelta(minutes=5))
            return Response({'status': 'success', 'access_token': str(access_token)})


class ChangePasswordAPIVIew(UpdateModelMixin, GenericAPIView):
    serializer_class = ChangePasswordSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        user = User.objects.get(id=self.request.user.id)
        return user

    def patch(self):
        serializer = self.get_serializer(data=self.request.data)
        if serializer.is_valid():
            new_password = self.request.data.get('new_password')
            confirming_new_password = self.request.data.get('confirming_new_password')
            if constant_time_compare(new_password, confirming_new_password):
                user = self.get_object()
                user.password = make_password(confirming_new_password)
                user.save()
                return Response({'status': 'success'}, status=status.HTTP_200_OK)
            else:
                return Response({'status': 'error'}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors)
