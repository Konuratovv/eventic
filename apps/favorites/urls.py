from django.urls import path

from .views import FavouriteEventAPIView, UnFavouriteEventAPIView, ListFavouritesAPIView

urlpatterns = [
    path('add_to_favourites/', FavouriteEventAPIView.as_view()),
    path('remove_from_favourites/', UnFavouriteEventAPIView.as_view()),
    path('list_favourites/', ListFavouritesAPIView.as_view())
]