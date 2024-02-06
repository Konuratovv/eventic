from django.urls import path

from .views import FavouriteEventAPIView, UnFavouriteEventAPIView

urlpatterns = [
    path('add_to_favourites/', FavouriteEventAPIView.as_view()),
    path('remove_from_favourites/', UnFavouriteEventAPIView.as_view()),
]