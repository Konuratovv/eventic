from rest_framework.serializers import ModelSerializer

from apps.profiles.models import User


class FavouriteEventSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ['favourites']
