from rest_framework.response import Response
from apps.notification.models import Notification
from apps.notification.serializers import NotiSerializer
from rest_framework import mixins   
from rest_framework.viewsets import GenericViewSet



class NotificationsAPIViewSet(GenericViewSet,
                                mixins.ListModelMixin,
                                mixins.RetrieveModelMixin,
                                mixins.CreateModelMixin,
                                mixins.UpdateModelMixin,
                                mixins.DestroyModelMixin):
    queryset = Notification.objects.all()
    serializer_class = NotiSerializer

    def get_object(self):
        event_id = self.kwargs['pk']
        return Notification.objects.filter(id=event_id).first()

    def get(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
