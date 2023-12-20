from apps.profiles.models import Organizer, Follow

from apps.profiles.models import User
from rest_framework.serializers import ModelSerializer


class ProfileSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'description', 'city', 'profile_picture', 'email']


class OrganizerSerializer(ModelSerializer):
    class Meta:
        model = Organizer
        exclude = ['code']


class FollowSerializer(ModelSerializer):
    class Meta:
        model = Follow
        fields = '__all__'

