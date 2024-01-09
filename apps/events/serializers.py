from rest_framework import serializers
from .models import Category, EventDate, BaseEvent, EventWeek, Interests, EventBanner, TemporaryEvent, PermanentEvent

from ..locations.models import Address, City
from ..profiles.models import Organizer


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = "__all__"


class InterestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Interests
        fields = "__all__"


class EventDateSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventDate
        fields = "__all__"


class EventWeekSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventWeek
        fields = '__all__'


class EventBannerSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventBanner
        fields = '__all__'


class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = ('address_name',)


class CityAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = City
        fields = ('city_name',)


class OrganizerEventSerializer(serializers.ModelSerializer):
    event_dates = EventDateSerializer(many=True, source='temporaryevent.dates')
    event_weeks = EventWeekSerializer(many=True, source='permanentevent.weeks')
    organizer_title = serializers.CharField(source='organizer.title', read_only=True) # это для проверки потом нужно удалить

    class Meta:
        model = BaseEvent
        fields = ('id', 'banners', 'title', 'price', 'event_dates', 'event_weeks', 'organizer_title',)


class OrganizerSerializer(serializers.ModelSerializer):
    events = OrganizerEventSerializer(many=True, read_only=True, source='baseevent_set')
    class Meta:
        model = Organizer
        fields = ('title', 'back_img', 'events',)


# class OrganizerNextEventSerializer(serializers.ModelSerializer):
#     events = OrganizerEventSerializer(many=True, read_only=True, source='events')
#
#     class Meta:
#         model = Organizer
#         fields = ('events',)


class BaseEventSerializer(serializers.ModelSerializer):
    category = CategorySerializer(many=True)
    interests = InterestSerializer(many=True)
    banners = EventBannerSerializer(many=True)
    organizer = OrganizerSerializer(read_only=True)
    city = CityAddressSerializer(read_only=True)
    address = AddressSerializer(read_only=True)
    event_dates = EventDateSerializer(many=True, source='temporaryevent.dates')
    event_weeks = EventWeekSerializer(many=True, source='permanentevent.weeks')

    class Meta:
        model = BaseEvent
        fields = (
            'id',
            'title',
            'description',
            'language',
            'banners',
            'event_dates',
            'event_weeks',
            'price',
            'category',
            'interests',
            'organizer',
            'address',
            'city',
        )


class DetailEventSerializer(serializers.ModelSerializer):
    interests = InterestSerializer(many=True)
    banners = EventBannerSerializer(many=True)
    address = AddressSerializer(read_only=True)
    organizer = OrganizerSerializer(read_only=True)
    # organizer_next_event = OrganizerNextEventSerializer(read_only=True)
    event_dates = EventDateSerializer(many=True, source='temporaryevent.dates')
    event_weeks = EventWeekSerializer(many=True, source='permanentevent.weeks')

    class Meta:
        model = BaseEvent
        fields = (
            'id',
            'title',
            'description',
            'banners',
            'event_dates',
            'event_weeks',
            'price',
            'interests',
            'organizer',
            'address',
            # 'organizer_next_event',
        )


