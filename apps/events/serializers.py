from rest_framework import serializers
from .models import Category, EventDate, BaseEvent, EventWeek, Interests, EventBanner

from ..locations.models import Address, City
from ..profiles.models import Organizer, FollowOrganizer, User

from datetime import datetime, timedelta


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


class DetailEventSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    interests = InterestSerializer(many=True)
    banners = EventBannerSerializer(many=True)
    address = AddressSerializer(read_only=True)
    organizer = OrganizerSerializer(read_only=True)
    event_dates = EventDateSerializer(many=True, source='temporaryevent.dates')
    event_weeks = EventWeekSerializer(many=True, source='permanentevent.weeks')
    next_events_org = serializers.SerializerMethodField()
    related_events_by_interest = serializers.SerializerMethodField()
    event_type = serializers.SerializerMethodField(read_only=True)
    is_notified = serializers.BooleanField(default=False)
    is_free = serializers.SerializerMethodField(read_only=True)
    average_time = serializers.SerializerMethodField()

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
            'is_free',
            'average_time',
            'price',
            'is_free',
            'category',
            'interests',
            'organizer',
            'address',
            'next_events_org',
            'related_events_by_interest',
            'is_notified',
        )

    def to_representation(self, instance):
        data = super().to_representation(instance)
        request = self.context.get('request')
        user = User.objects.get(id=request.user.id)
        is_subscribed = user.events.filter(pk=instance.id).exists()
        data['is_notified'] = is_subscribed
        return data

    def get_next_events_org(self, obj):
        """
        Возвращает список событий связанных с этим организатором,
        В детейле относится к 'Другие мероприятия организатора'
        """
        organizer = obj.organizer
        if organizer:
            now = datetime.now()

            # Получаем все временные события этого организатора, которые ещё не начались
            upcoming_temporary_events = BaseEvent.objects.filter(
                organizer=organizer,
                temporaryevent__dates__date__gt=now
            ).exclude(id=obj.id)

            # Получаем все постоянные события этого организатора
            permanent_events = BaseEvent.objects.filter(
                organizer=organizer,
                permanentevent__isnull=False
            ).exclude(id=obj.id)

            # Получаем прошедшие временные события
            past_temporary_events = BaseEvent.objects.filter(
                organizer=organizer,
                temporaryevent__dates__date__lt=now
            ).exclude(id=obj.id)

            # Объединяем списки событий, сначала будущие, затем постоянные, потом прошедшие
            related_events = list(upcoming_temporary_events[:5])
            if len(related_events) < 5:
                related_events += list(permanent_events[:5 - len(related_events)])
            if len(related_events) < 5:
                related_events += list(past_temporary_events[:5 - len(related_events)])

            if related_events:
                return OrganizerEventSerializer(related_events, many=True).data
        return []

    def get_related_events_by_interest(self, obj):
        """
        Возвращает список событий связанных с тегами (интересами),
        В детейле относится к 'Возможно вас также заинтересуют'
        """
        now = datetime.now()
        interests = obj.interests.all()

        # Ищем события с теми же интересами (как временные, так и постоянные)
        related_temporary_events = BaseEvent.objects.filter(
            interests__in=interests,
            temporaryevent__dates__date__gt=now
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
        """ Отображение типа evtenta в ответе """
        if hasattr(obj, 'temporaryevent'):
            return "temporary"
        elif hasattr(obj, 'permanentevent'):
            return "permanent"

    def get_is_free(self, obj):
        """
        Проверка поля is_free, чтобы определить,
        бесплатное мероприятие или нет, не анализируя саму цену.
        Например, показывать метку "Бесплатно" для мероприятий, у которых is_free равно True.
        """
        return obj.price == 0.0

    def get_average_time(self, obj):
        if hasattr(obj, 'temporaryevent'):
            durations = []
            for event_date in obj.temporaryevent.dates.all():
                start_datetime = datetime.combine(event_date.date, event_date.start_time)
                end_datetime = datetime.combine(event_date.date, event_date.end_time)
                if end_datetime < start_datetime:
                    end_datetime += timedelta(days=1)  # Добавляем 24 часа, если время окончания меньше времени начала
                duration = end_datetime - start_datetime
                durations.append(duration)

            if durations:
                avg_duration = sum(durations, timedelta()) / len(durations)
                total_seconds = int(avg_duration.total_seconds())
                hours = total_seconds // 3600
                minutes = (total_seconds % 3600) // 60
                return f"{hours} ч {minutes} мин"
            return "Нет данных"

        elif hasattr(obj, 'permanentevent'):
            total_duration = timedelta()
            count = 0
            for week in obj.permanentevent.weeks.all():
                start_time = datetime.combine(datetime.today(), week.start_time)
                end_time = datetime.combine(datetime.today(), week.end_time)
                if end_time < start_time:
                    end_time += timedelta(days=1)  # Добавляем 24 часа, если время окончания меньше времени начала
                duration = end_time - start_time
                total_duration += duration
                count += 1

            if count > 0:
                avg_duration = total_duration / count
                total_seconds = int(avg_duration.total_seconds())
                hours = total_seconds // 3600
                minutes = (total_seconds % 3600) // 60
                return f"{hours} ч {minutes} мин"
            return "Нет данных"
        return None

    
class EventAddressUpdateSerializer(serializers.ModelSerializer):
    address = AddressSerializer()

    class Meta:
        model = BaseEvent
        fields = ['id', 'address']
