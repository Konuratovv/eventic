from django.urls import path
from apps.users.views import RegisterAPIView, LoginViewSet, VerifyAPIView
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path('register/', RegisterAPIView.as_view()),
    path('login/', LoginViewSet.as_view()),
    path('refresh/', TokenRefreshView.as_view()),
    path('verify/', VerifyAPIView.as_view())
]
