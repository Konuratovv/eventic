from django.urls import path

from apps.users.views import RegisterAPIView, LoginViewSet
from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView

urlpatterns = [
    path('register/', RegisterAPIView.as_view()),
    path('login/', LoginViewSet.as_view()),
    path('refresh/', TokenRefreshView.as_view()),
    path('verify/', TokenVerifyView.as_view()),
]
