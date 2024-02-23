from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework import viewsets

from apps.invitations.models import Category, Contact, Image
from apps.invitations.serializers import CategorySerialzer, ContactSerializer, ImageSerializer


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

    def perform_create(self, serializer):
        serializer.save(user=self.request.user.baseprofile.user)


class ContactDeleteAPIView(generics.DestroyAPIView):
    serializer_class = ContactSerializer
    permission_classes = [IsAuthenticated]
    queryset = Contact.objects.all()


class ImageAPIView(generics.ListAPIView):
    queryset = Image.objects.all()
    serializer_class = ImageSerializer
    permission_classes = [IsAuthenticated]
