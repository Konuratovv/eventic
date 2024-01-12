from apps.events.models import BaseEvent, EventDate, EventWeek, TemporaryEvent, PermanentEvent, Interests
from apps.events.serializers import EventBannerSerializer
from apps.locations.models import Address
from apps.profiles.models import Organizer, FollowOrganizer, ViewedEvent

from apps.profiles.models import User
from rest_framework.serializers import ModelSerializer
from rest_framework import serializers

from apps.users.models import CustomUser


class ProfileSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'description', 'city', 'profile_picture', 'email', 'city', ]


class OrganizerSerializer(ModelSerializer):
    is_follow = serializers.BooleanField(default=False)

    class Meta:
        model = Organizer
        exclude = ['code', 'password', 'groups', 'user_permissions', 'last_login', 'is_superuser', 'is_staff',
                   'is_verified']


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


class MainEventDateSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventDate
        fields = "__all__"


class MainEventWeekSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventWeek
        fields = '__all__'


class AddressEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = '__all__'


class InterestsEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Interests
        fields = '__all__'


class MainBaseEventSerializer(serializers.ModelSerializer):
    banners = EventBannerSerializer(many=True)
    event_weeks = MainEventWeekSerializer(many=True, source='permanentevent.weeks')
    event_dates = MainEventDateSerializer(many=True, source='temporaryevent.dates')
    is_follow = serializers.BooleanField(default=False)

    class Meta:
        model = BaseEvent
        fields = [
            'id',
            'banners',
            'title',
            'price',
            'organizer',
            'event_weeks',
            'event_dates',
            'is_follow'
        ]


class LastViewedEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = ViewedEvent
        fields = ['event']


class LastViewedEventReadSerializer(serializers.ModelSerializer):
    event = MainBaseEventSerializer(read_only=True)

    class Meta:
        model = ViewedEvent
        fields = ['event']


class TemporaryEventSerializer(MainBaseEventSerializer):
    class Meta:
        model = TemporaryEvent
        fields = '__all__'


class PermanentEventSerializer(MainBaseEventSerializer):
    class Meta:
        model = PermanentEvent
        fields = '__all__'
