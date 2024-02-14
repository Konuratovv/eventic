from django.db.models import Q
from django.shortcuts import render, get_object_or_404

from rest_framework.generics import RetrieveAPIView, CreateAPIView, ListAPIView
from rest_framework.permissions import IsAuthenticated

from .models import OrganizerEventNotification
from .serializers import NotificationSerializer


class Notifications(ListAPIView):
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user.baseprofile.user
        notifications = OrganizerEventNotification.objects.filter(event__organizer__in=user.organizers.all())
        return notifications



