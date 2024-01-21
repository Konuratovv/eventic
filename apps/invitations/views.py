from django.shortcuts import render

from rest_framework.viewsets import GenericViewSet
from rest_framework import mixins
# from rest_framework.permissions import IsAuthenticated

from apps.invitations.models import Invitation, Recipient, Category
from apps.invitations.permissions import InvitationPermission
from apps.invitations.serializers import InvitationSerializer, RecipientSerializer, CategorySerializer

class InvitationAPIViewSet(GenericViewSet,
                            mixins.ListModelMixin,
                            mixins.RetrieveModelMixin,
                            mixins.CreateModelMixin,
                            mixins.UpdateModelMixin,
                            mixins.DestroyModelMixin):
    queryset = Invitation.objects.all()
    serializer_class = InvitationSerializer
    permission_classes = [InvitationPermission]


class RecipientAPIViewSet(GenericViewSet,
                            mixins.ListModelMixin,
                            mixins.RetrieveModelMixin,
                            mixins.CreateModelMixin,
                            mixins.UpdateModelMixin,
                            mixins.DestroyModelMixin):
    queryset = Recipient.objects.all()
    serializer_class = RecipientSerializer
    permission_classes = [InvitationPermission]


class CategoryAPIViewSet(GenericViewSet,
                            mixins.ListModelMixin,
                            mixins.RetrieveModelMixin,
                            mixins.CreateModelMixin,
                            mixins.UpdateModelMixin,
                            mixins.DestroyModelMixin):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [InvitationPermission]
    
