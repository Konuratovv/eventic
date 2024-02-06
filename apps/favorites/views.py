from django.core.exceptions import ObjectDoesNotExist
from rest_framework.generics import CreateAPIView, DestroyAPIView, ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.events.models import BaseEvent
from apps.favorites.serializers import FavouriteEventSerializer
from apps.profiles.models import User


# Create your views here.

class FavouriteEventAPIView(CreateAPIView):
    serializer_class = FavouriteEventSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        obj_user = request.user.baseprofile.user

        event_id = request.data['favourites']
        try:
            obj_event = BaseEvent.objects.get(id=event_id)
        except ObjectDoesNotExist:
            return Response({"status": "error"})

        obj_user.favourites.add(obj_event)
        obj_user.save()
        return Response({"status": "success"})


class UnFavouriteEventAPIView(DestroyAPIView):
    serializer_class = FavouriteEventSerializer
    permission_classes = [IsAuthenticated]

    def delete(self, request, *args, **kwargs):
        user_id = request.user.id
        obj_user = User.objects.get(id=user_id)
        event_id = request.data['favourites']
        try:
            obj_event = BaseEvent.objects.get(id=event_id)
        except ObjectDoesNotExist:
            return Response({"status": "error"})
        obj_user.favourites.remove(obj_event)
        return Response({"status": "success"})
