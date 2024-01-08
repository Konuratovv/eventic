from rest_framework import serializers
from .models import Category, EventDate, BaseEvent, EventWeek, Interests, EventBanner, TemporaryEvent, PermanentEvent

from ..locations.models import Address


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


class BaseEventSerializer(serializers.ModelSerializer):
    category = CategorySerializer(many=True)
    interests = InterestSerializer(many=True)
    banners = EventBannerSerializer(many=True)

    organizer_title = serializers.CharField(source='organizer.title', read_only=True)
    address_city = serializers.CharField(source='address.city', read_only=True)
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
            'organizer_title',
            'address',
            'address_city',
        )


class TemporaryEventSerializer(BaseEventSerializer):
    dates = EventDateSerializer(many=True, read_only=True, source='dates')

    class Meta(BaseEventSerializer.Meta):
        model = TemporaryEvent
        fields = BaseEventSerializer.Meta.fields + ('dates',)


class PermanentEventSerializer(BaseEventSerializer):
    weeks = EventWeekSerializer(many=True, read_only=True, source='weeks')

    class Meta(BaseEventSerializer.Meta):
        model = PermanentEvent
        fields = BaseEventSerializer.Meta.fields + ('weeks',)
