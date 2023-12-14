from django.urls import path

from apps.profiles.views import ProfileViewSet

urlpatterns = [
    path('profile/', ProfileViewSet.as_view())
]
