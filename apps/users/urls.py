from django.urls import path
from apps.users.views import RegisterViewSet, LoginViewSet
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path('register/', RegisterViewSet.as_view()),
    path('login/', LoginViewSet.as_view()),
    path('refresh/', TokenRefreshView.as_view())
]
