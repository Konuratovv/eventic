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


class SubscribersUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = FollowOrganizer
        fields = '__all__'


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
