from apps.events.models import BaseEvent, EventDate, EventWeek, TemporaryEvent, PermanentEvent, Interests
from apps.events.serializers import EventBannerSerializer, AddressSerializer
from apps.locations.models import Address
from apps.profiles.models import Organizer, FollowOrganizer, ViewedEvent, PhoneNumber, Email, SocialLink

from apps.profiles.models import User
from rest_framework.serializers import ModelSerializer
from rest_framework import serializers

from apps.users.models import CustomUser


class ProfileSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'description', 'city', 'profile_picture', 'email', 'city', ]


class PhoneNumberSerializer(ModelSerializer):
    class Meta:
        model = PhoneNumber
        fields = '__all__'


class EmailSerializer(ModelSerializer):
    class Meta:
        model = Email
        fields = '__all__'


class SocialLinkSerializer(ModelSerializer):
    class Meta:
        model = SocialLink
        fields = '__all__'


class OrganizerDetailSerializer(ModelSerializer):
    is_followed = serializers.BooleanField(default=False)
    address = AddressSerializer(many=True)
    phone_numbers = PhoneNumberSerializer(many=True)
    emails = EmailSerializer(many=True)
    social_links = SocialLinkSerializer(many=True)

    class Meta:
        model = Organizer
        exclude = ['code', 'password', 'groups', 'user_permissions', 'last_login', 'is_superuser', 'is_staff',
                   'is_verified', 'email']


class MainOrganizerSerializer(ModelSerializer):
    is_followed = serializers.BooleanField(default=False)

    class Meta:
        model = Organizer
        fields = ['id', 'is_followed', 'profile_picture', 'title']


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
    is_favourite = serializers.BooleanField(default=False)

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
            'is_favourite'
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
    pass


class PermanentEventSerializer(MainBaseEventSerializer):
    pass
