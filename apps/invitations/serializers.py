from rest_framework import serializers

from apps.invitations.models import Category, Contact, Image
from apps.profiles.models import User


class CategorySerialzer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'


class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = [
            'id',
            'name',
        ]


class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = '__all__'
