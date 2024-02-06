from rest_framework import serializers

from apps.profiles.models import User


class FavouriteEventSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ['favourites']

