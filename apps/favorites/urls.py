from django.urls import path

from .views import FavouriteEventAPIView, UnFavouriteEventAPIView

urlpatterns = [
    path("favourite_event/", FavouriteEventAPIView.as_view()),
    path("un_favourite_event/", UnFavouriteEventAPIView.as_view()),
]