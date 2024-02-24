from django.core.exceptions import ObjectDoesNotExist
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.invitations.models import Category, Contact, Image
from apps.invitations.serializers import CategorySerialzer, ContactSerializer, ImageSerializer
from apps.profiles.models import User


class CategoryAPIView(generics.ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerialzer
    permission_classes = [IsAuthenticated]


class ContactAPIView(generics.ListCreateAPIView):
    serializer_class = ContactSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user.baseprofile.user
        return Contact.objects.filter(user=user)

    def post(self, request, *args, **kwargs):
        name = self.request.data.get('name')
        try:
            user = User.objects.get(id=self.request.user.baseprofile.user.id)
        except ObjectDoesNotExist:
            return Response({'status': 'user is not found'}, status=status.HTTP_400_BAD_REQUEST)
        Contact.objects.create(name=name, user=user)
        return Response({'status': 'success'})


class ContactDeleteAPIView(generics.DestroyAPIView):
    serializer_class = ContactSerializer
    permission_classes = [IsAuthenticated]

    def delete(self, request, *args, **kwargs):
        try:
            contact = Contact.objects.get(id=kwargs.get('pk'))
            contact.delete()
        except ObjectDoesNotExist:
            return Response({'status': 'contact is not fount'}, status=status.HTTP_400_BAD_REQUEST)
        return Response({'status': 'success'})


class ImageAPIView(generics.ListAPIView):
    queryset = Image.objects.all()
    serializer_class = ImageSerializer
    permission_classes = [IsAuthenticated]
