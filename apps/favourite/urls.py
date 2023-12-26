from django.urls import path

from .views import EventFavoriteAPIView

urlpatterns = [
    path('api_favorite/', EventFavoriteAPIView.as_view(),name='favorite'),
]