from django.urls import path

from apps.profiles.views import FollowAPIView
from apps.users.views import RegisterAPIView, LoginViewSet, VerifyAPIView, SendCodeAPIView
from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView

urlpatterns = [
    path('register/', RegisterAPIView.as_view()),
    path('login/', LoginViewSet.as_view()),
    path('refresh/', TokenRefreshView.as_view()),
    path('verify-email/', VerifyAPIView.as_view()),
    path('send-code/', SendCodeAPIView.as_view()),
    path('verify/', TokenVerifyView.as_view()),
    path('follow/', FollowAPIView.as_view()),
]
