from django.urls import path

from apps.users.views import RegisterAPIView, LoginAPIView, SendResetAPiView, CheckResetCodeAPIView, \
    ChangePasswordAPIVIew, VerifyEmailAPIView, SendVerifyCodeAPIView
from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView

urlpatterns = [
    path('register/', RegisterAPIView.as_view()),
    path('login/', LoginAPIView.as_view()),
    path('refresh/', TokenRefreshView.as_view()),
    path('verify/', TokenVerifyView.as_view()),
    path('send_reset_code/', SendResetAPiView.as_view()),
    path('check_reset_code/', CheckResetCodeAPIView.as_view()),
    path('change_password/', ChangePasswordAPIVIew.as_view()),
    path('verify/email/', VerifyEmailAPIView.as_view()),
    path('send_verify_code/', SendVerifyCodeAPIView.as_view())
]
