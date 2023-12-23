from django.shortcuts import render

from rest_framework.generics import RetrieveAPIView


from .models import Notification


class Notifications(RetrieveAPIView) :
    queryset = Notification.objects.all()

    def get_object(self):
        event_id = self.kwargs['pk']
        return Notification.objects.filter(event__id=event_id).first()

    def retrieve(self, request, *args, **kwargs):
        return self.get_queryset().filter(evetn__user_id=self.request.user.id, is_read=False).exists()
