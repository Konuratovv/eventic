from apps.events.models import Event
from apps.profiles.models import Organizer, FollowOrganizer

from apps.profiles.models import User
from rest_framework.serializers import ModelSerializer
from rest_framework import serializers


class ProfileSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'description', 'city', 'profile_picture', 'email']


class OrganizerSerializer(ModelSerializer):
    class Meta:
        model = Organizer
        exclude = ['code']


class FollowOrganizerSerializer(ModelSerializer):
    class Meta:
        model = FollowOrganizer
        fields = ['following']


class FollowEventSerializer(ModelSerializer):

    class Meta:
        model = User
        fields = ['events']
