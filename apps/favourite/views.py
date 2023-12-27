from django.shortcuts import render
from rest_framework.viewsets import GenericViewSet
from rest_framework import mixins
from .models import EventFavorite
from .serializers import EventFavoriteSerializer


class EventFavoriteAPIView(GenericViewSet,
                           mixins.CreateModelMixin,
                           mixins.DestroyModelMixin,
                           mixins.UpdateModelMixin,
                           ):
    queryset = EventFavorite.objects.all()
    serializer_class = EventFavoriteSerializer

    def perform_create(self, serializer):
        return serializer.save(user=self.request.user)
