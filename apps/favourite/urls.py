from django.urls import path

from .views import EventFavoriteAPIView

urlpatterns = [
    path('api_favorite/', EventFavoriteAPIView.as_view({'post': 'create', 'delete': 'destroy', 'put': 'update'}),
         name='favorite'),
]
