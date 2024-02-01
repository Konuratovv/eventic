from django.urls import path

from .views import CityListAPIView
urlpatterns = [
    path('city-list/', CityListAPIView.as_view()),
]
