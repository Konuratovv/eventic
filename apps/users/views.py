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
    LoginSerializer
from apps.users.utils import send_verification_mail


class RegisterAPIView(CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        device_token = User.objects.filter(device_token=self.request.data.get('device_token')).exists()
        if device_token:
            user = User.objects.get(device_token=self.request.data.get('device_token'))

            def is_email_unique(email, excluded_user_id):
                queryset = User.objects.filter(email=email)
                queryset2 = queryset.exclude(id=excluded_user_id)
                return not queryset2.exists()

            if is_email_unique(self.request.data['email'], user.id):

                user.email = self.request.data.get('email')
                user.first_name = self.request.data.get('first_name')
                user.last_name = self.request.data.get('last_name')

                if self.request.data.get('password') == self.request.data.get('confirm_password'):
                    user.password = make_password(self.request.data.get('password'))
                    user.save()
                    send_verification_mail(user.email)
                    return Response({'status': 'success'})

                return Response({'status': 'error'}, status=status.HTTP_400_BAD_REQUEST)
            return Response({'status': 'error'}, status=status.HTTP_400_BAD_REQUEST)

        if serializer.is_valid(raise_exception=True):
            user = User.objects.create_user(
                email=serializer.validated_data['email'],
                first_name=serializer.validated_data['first_name'],
                last_name=serializer.validated_data['last_name'],
                password=serializer.validated_data['password'],
                device_token=serializer.validated_data['device_token'],
            )
            send_verification_mail(user.email)
            return Response({"status": 'success'})

        return Response({'status': 'error'}, status=status.HTTP_400_BAD_REQUEST)


class LoginAPIView(RegisterAPIView):
    permission_classes = [AllowAny]
    serializer_class = LoginSerializer

    def get(self, request, *args, **kwargs):
        user = User.objects.filter(email=self.request.data.get('email'))
        if user.exists() and user[0].check_password(self.request.data.get('password')):
            if not user[0].is_verified:
                return Response({'status': 'user is not valid'})
            access_token = AccessToken.for_user(user[0])
            refresh_token = RefreshToken.for_user(user[0])
            return Response({'access_token': str(access_token), 'refresh_token': str(refresh_token)})
        return Response({'status': 'error'}, status=status.HTTP_400_BAD_REQUEST)


class VerifyEmailAPIView(UpdateModelMixin, GenericAPIView):
    serializer_class = CodeVerifyEmailSerializer

    def patch(self, request, *args, **kwargs):
        user = User.objects.filter(device_token=self.request.data.get('device_token'))
        verify_code = self.request.data.get('code')
        if user[0].code == verify_code:
            user[0].is_verified = True
            user[0].code = None
            user[0].save()
            return Response({'status': 'success'})
        return Response({'status': 'error'})


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
            return Response({'status': 'error'})
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
