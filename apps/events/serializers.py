from rest_framework import serializers
from .models import Category, EventDate, BaseEvent, EventWeek, Interests, EventBanner, TemporaryEvent, PermanentEvent

from ..locations.models import Address, City
from ..profiles.models import Organizer, FollowOrganizer

import datetime


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
    event_type = serializers.SerializerMethodField()

    class Meta:
        model = BaseEvent
        fields = ('id', 'title', 'price', 'banners', 'event_type', 'event_dates', 'event_weeks',)

    def to_representation(self, instance):
        """ Ограничиваем количество баннеров до одного """
        representation = super(OrganizerEventSerializer, self).to_representation(instance)
        banners_representation = representation.get('banners')
        if banners_representation:
            representation['banners'] = banners_representation[:1]
        return representation

    def get_event_type(self, obj):
        """ Вывод типа мероприятия в next_events_org и в related_events_by_interest """
        if hasattr(obj, 'temporaryevent'):
            return 'temporary'
        elif hasattr(obj, 'permanentevent'):
            return 'permanent'


class OrganizerSerializer(serializers.ModelSerializer):
    is_followed = serializers.SerializerMethodField()

    class Meta:
        model = Organizer
        fields = ('title', 'back_img', 'is_followed',)

    def get_is_followed(self, obj):
        user = self.context.get('request').user
        try:
            return FollowOrganizer.objects.get(follower=user, following=obj).is_followed
        except FollowOrganizer.DoesNotExist:
            return False


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
    related_events_by_interest = serializers.SerializerMethodField()
    event_type = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = BaseEvent
        fields = (
            'id',
            'title',
            'description',
            'banners',
            'event_type',
            'event_dates',
            'event_weeks',
            'price',
            'interests',
            'organizer',
            'address',
            'next_events_org',
            'related_events_by_interest',

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
            now = datetime.datetime.now()
            events = BaseEvent.objects.filter(
                organizer=organizer,
                temporaryevent__dates__start_date__gt=now
            ).exclude(id=obj.id)[:5]

            if events.exists():  # Проверяем, существуют ли события
                return OrganizerEventSerializer(events, many=True).data
        return []

    def get_related_events_by_interest(self, obj):
        now = datetime.datetime.now()
        interests = obj.interests.all()

        # Ищем события с теми же интересами (как временные, так и постоянные)
        related_temporary_events = BaseEvent.objects.filter(
            interests__in=interests,
            temporaryevent__dates__start_date__gt=now
        ).exclude(id=obj.id)  # временные

        related_permanent_events = BaseEvent.objects.filter(
            interests__in=interests,
            permanentevent__isnull=False
        ).exclude(id=obj.id)  # постоянные

        # Объединяем оба QuerySet
        related_events = related_temporary_events | related_permanent_events
        related_events = related_events.distinct()[:5]  # distinct для удаления дубликатов

        if related_events.exists():
            return OrganizerEventSerializer(related_events, many=True).data
        return []

    def get_event_type(self, obj):
        if hasattr(obj, 'temporaryevent'):
            return "temporary"
        elif hasattr(obj, 'permanentevent'):
            return "permanent"

