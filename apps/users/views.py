from datetime import timedelta

from django.contrib.auth.hashers import make_password
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import status
from rest_framework.mixins import UpdateModelMixin
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken
from django.utils.crypto import constant_time_compare
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated

from rest_framework.generics import CreateAPIView, GenericAPIView
from apps.profiles.models import User
from apps.users.models import CustomUser
from apps.profiles.serializer import SendResetCodeSerializer, ChangePasswordSerializer
from apps.users.serializer import RegisterSerializer, CodeSerializer, CodeVerifyEmailSerializer, \
    LoginSerializer, SendEmailVerifyCodeSerializer
from config.settings.base import DEBUG
from apps.users.utils import send_verification_mail
from apps.notifications.tasks import send_verification_mail_task


class RegisterAPIView(CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            user = User.objects.create_user(
                email=serializer.validated_data['email'],
                first_name=serializer.validated_data['first_name'],
                last_name=serializer.validated_data['last_name'],
                password=serializer.validated_data['password'],
            )
            if DEBUG:
                send_verification_mail(user.email)
            else:
                send_verification_mail_task.delay(user.email)
            return Response({"status": 'success'})
        return Response({'status': 'error'}, status=status.HTTP_400_BAD_REQUEST)


class SendVerifyCodeAPIView(UpdateModelMixin, GenericAPIView):
    serializer_class = SendEmailVerifyCodeSerializer
    permission_classes = [AllowAny]

    def patch(self, request, *args, **kwargs):
        user = User.objects.filter(email=self.request.data.get('email'))
        if user.exists():
            if DEBUG:
                send_verification_mail(user[0].email)
            else:
                send_verification_mail_task.delay(user[0].email)
            return Response({'status': 'success'})
        return Response({'status': 'error'}, status=status.HTTP_400_BAD_REQUEST)


class LoginAPIView(CreateAPIView):
    permission_classes = [AllowAny]
    serializer_class = LoginSerializer

    def post(self, request, *args, **kwargs):
        user = User.objects.filter(email=self.request.data.get('email'))
        if user.exists() and user[0].check_password(self.request.data.get('password')):
            if not user[0].is_verified:
                if DEBUG:
                    send_verification_mail(user[0].email)
                else:
                    send_verification_mail_task.delay(user[0].email)
                return Response({'status': 'user is not valid'}, status=status.HTTP_400_BAD_REQUEST)
            access_token = AccessToken.for_user(user[0])
            refresh_token = RefreshToken.for_user(user[0])
            return Response({'access_token': str(access_token), 'refresh_token': str(refresh_token)})
        return Response({'status': 'error'}, status=status.HTTP_401_UNAUTHORIZED)


class VerifyEmailAPIView(UpdateModelMixin, GenericAPIView):
    serializer_class = CodeVerifyEmailSerializer

    def patch(self, request, *args, **kwargs):
        user = User.objects.filter(email=self.request.data.get('email')).first()
        verify_code = self.request.data.get('code')
        if user.code == verify_code:
            user.is_verified = True
            user.code = None
            user.save()
            access_token = AccessToken.for_user(user)
            refresh_token = RefreshToken.for_user(user)
            return Response({'access_token': str(access_token), 'refresh_token': str(refresh_token)})
        return Response({'status': 'error'}, status=status.HTTP_400_BAD_REQUEST)


class SendResetAPiView(UpdateModelMixin, GenericAPIView):
    serializer_class = SendResetCodeSerializer

    def get_object(self):
        user = CustomUser.objects.get(email=self.request.data.get('email'))
        return user

    def patch(self, *args, **kwargs):
        try:
            email = self.get_object().email
        except ObjectDoesNotExist:
            return Response({'status': 'error'}, status=status.HTTP_400_BAD_REQUEST)
        send_verification_mail(email)
        return Response({'status': 'success'}, status=status.HTTP_200_OK)


class CheckResetCodeAPIView(UpdateModelMixin, GenericAPIView):
    serializer_class = CodeSerializer

    def patch(self, *args, **kwargs):
        code = self.request.data.get('code')
        email = self.request.data.get('email')
        if code is None:
            return Response({'status': 'error'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            user = CustomUser.objects.get(email=email)
            if user.code == code:
                user.code = None
                user.save()
                access_token = AccessToken.for_user(user)
                access_token.set_exp(lifetime=timedelta(minutes=5))
                return Response({'status': 'success', 'access_token': str(access_token)})
            return Response({'status': 'error'})
        except ObjectDoesNotExist:
            return Response({'status': 'error'}, status=status.HTTP_400_BAD_REQUEST)


class ChangePasswordAPIVIew(UpdateModelMixin, GenericAPIView):
    serializer_class = ChangePasswordSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        user = User.objects.get(id=self.request.user.id)
        return user

    def patch(self, *args, **kwargs):
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
