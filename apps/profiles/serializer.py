from apps.events.models import BaseEvent, PermanentEvent, TemporaryEvent
from apps.events.serializers import EventWeekSerializer, EventDateSerializer
from apps.profiles.models import Organizer, FollowOrganizer

from apps.profiles.models import User
from rest_framework.serializers import ModelSerializer
from rest_framework import serializers

from apps.users.models import CustomUser


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


class SendResetCodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['email']


class ChangePasswordSerializer(serializers.Serializer):
    new_password = serializers.CharField(max_length=30)
    confirming_new_password = serializers.CharField(max_length=30)

    class Meta:
        fields = ['new_password', 'confirming_new_password']


class BaseEventSerializer(serializers.ModelSerializer):

    class Meta:
        model = BaseEvent
        fields = '__all__'


class PermanentEventSerializer(serializers.ModelSerializer):
    weeks = EventWeekSerializer(many=True)

    class Meta:
        model = PermanentEvent
        fields = '__all__'


class TemporaryEventSerializer(serializers.ModelSerializer):
    dates = EventDateSerializer(many=True)

    class Meta:
        model = TemporaryEvent
        fields = '__all__'
