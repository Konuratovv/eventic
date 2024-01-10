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
    banners = EventBannerSerializer(many=True, read_only=True)

    class Meta:
        model = BaseEvent
        fields = ('id', 'banners', 'title', 'price', 'event_dates', 'event_weeks', 'banners',)


class OrganizerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organizer
        fields = ('title', 'back_img',)


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
    event_dates = EventDateSerializer(many=True, source='temporaryevent.dates')
    event_weeks = EventWeekSerializer(many=True, source='permanentevent.weeks')
    next_events_org = serializers.SerializerMethodField()

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
            'next_events_org',

        )

    def get_next_events_org(self, obj):
        """
        Метод в сериализаторе DetailEventSerializer извлекает и возвращает список событий,
        организованных тем же организатором, что и текущее событие (obj),
        за исключением самого этого события, используя сериализатор OrganizerEventSerializer.
        Обеспечивает добавление информации о связанных мероприятиях в API-ответ.
        """
        organizer = obj.organizer
        if organizer:
            events = BaseEvent.objects.filter(organizer=organizer).exclude(id=obj.id)
            return OrganizerEventSerializer(events, many=True).data
        return []
