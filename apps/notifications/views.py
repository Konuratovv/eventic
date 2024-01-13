from django.db.models import Q
from django.shortcuts import render, get_object_or_404

from rest_framework.generics import RetrieveAPIView, CreateAPIView,ListAPIView

from .models import Notification
from .serializers import NotificationSerializer


class Notifications(RetrieveAPIView) :
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer

    def get_object(self):
        event_id = self.kwargs['pk']
        return Notification.objects.filter(event__id=event_id).first()
    def get_notifications_for_user(user):

        notifications = Notification.objects.filter(Q (event__organizer__user=user)|Q (event__user=user))
        return notifications

# https://github.com/firebase/firebase-ios-sdk