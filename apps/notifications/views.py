
from django.shortcuts import render

from rest_framework.generics import RetrieveAPIView, CreateAPIView,ListAPIView
from rest_framework.permissions import IsAuthenticated
from .models import Notification
from ..profiles.models import FollowOrganizer


class Notifications(RetrieveAPIView) :
    queryset = Notification.objects.all()

    def get_object(self):
        event_id = self.kwargs['pk']
        return Notification.objects.filter(event__id=event_id).first()

    # def retrieve(self, request, *args, **kwargs):
    #     return self.get_queryset().filter(evetn__user_id=self.request.user.id, is_read=False).exists()



# class SentNotifApiView(ListAPIView):
#     permission_classes = [IsAuthenticated]
#     serializer_class =
#
#

