from rest_framework.response import Response
from apps.invitations.models import Invitation
from apps.invitations.serializers import InviSerializer
from rest_framework import mixins   
from rest_framework.viewsets import GenericViewSet



class NotificationsAPIViewSet(GenericViewSet,
                                mixins.ListModelMixin,
                                mixins.RetrieveModelMixin,
                                mixins.CreateModelMixin,
                                mixins.UpdateModelMixin,
                                mixins.DestroyModelMixin):
    queryset = Invitation.objects.all()
    serializer_class = InviSerializer

    def get_object(self):
        event_id = self.kwargs['pk']
        return Invitation.objects.filter(id=event_id).first()

    def get(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
