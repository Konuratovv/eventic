from apps.events.models import BaseEvent, EventDate, Interests, PermanentEventDays, \
    PermanentEvent
from apps.events.serializers import EventBannerSerializer, InterestSerializer, CategorySerializer
from apps.locations.models import Address
from apps.locations.serializers import CitySerializer
from apps.notifications.models import FollowOrg
from apps.profiles.models import Organizer, ViewedEvent, PhoneNumber, SocialLink, OrganizerAddress

from apps.profiles.models import User
from rest_framework.serializers import ModelSerializer
from rest_framework import serializers

from apps.users.models import CustomUser


class UpdateCitySerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ['city', ]


class ProfileSerializer(ModelSerializer):
    city = CitySerializer(read_only=True)

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'city', 'profile_picture', 'email', 'city']


class ChangeProfileNamesSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ['first_name', 'last_name']


class UserProfileStatistics(ModelSerializer):
    class Meta:
        model = User
        fields = ['favourites', 'events']


class ChangeUserPasswordSerializer(ModelSerializer):
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True)
    confirming_new_password = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = ['old_password', 'new_password', 'confirming_new_password', 'code']


class PhoneNumberSerializer(ModelSerializer):
    class Meta:
        model = PhoneNumber
        fields = '__all__'


class SocialLinkSerializer(ModelSerializer):
    class Meta:
        model = SocialLink
        fields = '__all__'


class OrganizerAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrganizerAddress
        fields = '__all__'


class MainOrganizerSerializer(ModelSerializer):
    is_followed = serializers.SerializerMethodField()

    class Meta:
        model = Organizer
        fields = ['id', 'profile_picture', 'title', 'is_followed']

    def get_is_followed(self, organizer):
        return organizer in self.context.get('followed_organizers')


class ListOrginizerSerializer(ModelSerializer):
    is_followed = serializers.SerializerMethodField()

    class Meta:
        model = Organizer
        fields = ['id', 'is_followed', 'profile_picture', 'title']

    def get_is_followed(self, organizer):
        return organizer in self.context.get('followed_organizers')


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


class PermanentEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = PermanentEvent
        fields = '__all__'


class MainEventWeekSerializer(serializers.ModelSerializer):
    class Meta:
        model = PermanentEventDays
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
    is_favourite = serializers.SerializerMethodField()

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
            'is_favourite',
            'followers',
        ]

    def get_is_favourite(self, event):
        return event in self.context.get('custom_user').favourites.all()


class UserFavouritesSerializer(serializers.ModelSerializer):
    banners = EventBannerSerializer(many=True)
    event_weeks = MainEventWeekSerializer(many=True, source='permanentevent.weeks')
    event_dates = MainEventDateSerializer(many=True, source='temporaryevent.dates')
    category = CategorySerializer()
    is_favourite = serializers.SerializerMethodField()
    is_free = serializers.SerializerMethodField()

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
            'is_favourite',
            'category',
            'is_free',
            'is_active'
        ]

    def get_is_favourite(self, event):
        user_obj = self.context.get('request').user.baseprofile.user
        return event.pk in user_obj.favourites.values_list('pk', flat=True)

    def get_is_free(self, event):
        return True if event.price == 0 else False


class DetailBaseEventSerializer(serializers.ModelSerializer):
    banners = EventBannerSerializer(many=True)
    event_weeks = MainEventWeekSerializer(many=True, source='permanentevent.weeks')
    event_dates = MainEventDateSerializer(many=True, source='temporaryevent.dates')
    is_favourite = serializers.SerializerMethodField()

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

    def get_is_favourite(self, events):
        user_obj = self.context.get('request').user.baseprofile.user
        return user_obj.favourites.filter(pk=events.pk).exists()


class OrganizerDetailSerializer(ModelSerializer):
    phone_numbers = PhoneNumberSerializer(many=True)
    social_links = SocialLinkSerializer(many=True)
    addresses = OrganizerAddressSerializer(many=True)
    interests = serializers.SerializerMethodField()
    is_followed = serializers.SerializerMethodField()

    class Meta:
        model = Organizer
        fields = [
            'id',
            'title',
            'email',
            'profile_picture',
            'back_img',
            'description',
            'is_followed',
            'phone_numbers',
            'social_links',
            'addresses',
            'interests'
        ]

    def get_interests(self, organizer):
        events = BaseEvent.objects.filter(organizer=organizer)
        interests = []

        for event in events:
            interests.extend(event.interests.all())
        interests = list(set(interests))
        serializer = InterestSerializer(interests, many=True)
        return serializer.data

    def get_is_followed(self, organizer):
        return organizer in self.context.get('followed_organizers')


class LastViewedEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = ViewedEvent
        fields = ['event']


class LastViewedEventReadSerializer(serializers.ModelSerializer):
    event = MainBaseEventSerializer()

    class Meta:
        model = ViewedEvent
        fields = ['event']


class ChangeUserPictureSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['profile_picture']


class AllMainBaseEventSerializer(serializers.ModelSerializer):
    banners = EventBannerSerializer(many=True)
    event_weeks = MainEventWeekSerializer(many=True, source='permanentevent.weeks')
    event_dates = MainEventDateSerializer(many=True, source='temporaryevent.dates')
    is_favourite = serializers.SerializerMethodField()

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
            'is_favourite',
        ]

    def get_is_favourite(self, event):
        return event in self.context.get('request').user.baseprofile.user.favourites.all()


class FollowOrganizerSerializer(serializers.ModelSerializer):
    class Meta:
        model = FollowOrg
        fields = ['organizer']


class GoogleOAuthSerializer(serializers.Serializer):
    google_token = serializers.CharField(max_length=1000)

    class Meta:
        fields = ['google_token']


class AppleOAuthSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']


class SendChangeEmailCodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['code']


class DeleteUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'
