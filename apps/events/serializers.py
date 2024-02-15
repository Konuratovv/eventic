from rest_framework import serializers
from .models import Category, EventDate, BaseEvent, Interests, EventBanner, PermanentEvent, PermanentEventDays

from ..locations.models import City
from ..locations.serializers import CitySerializer
from ..profiles.models import Organizer

from datetime import date
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
        model = PermanentEventDays
        fields = '__all__'


class EventBannerSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventBanner
        fields = '__all__'


class CityAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = City
        fields = ('city_name',)


class PermanentEventWeeksSerializer(serializers.ModelSerializer):
    weeks = EventWeekSerializer(many=True, read_only=True)

    class Meta:
        model = PermanentEvent
        fields = ['weeks']


class OrganizerEventSerializer(serializers.ModelSerializer):
    event_dates = EventDateSerializer(many=True, source='temporaryevent.dates')
    event_weeks = PermanentEventWeeksSerializer(source='permanentevent', read_only=True)
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
        fields = ('id', 'title', 'profile_picture', 'back_img', 'is_followed',)

    def get_is_followed(self, obj):
        return obj in self.context.get('request').user.baseprofile.user.organizers.all()


class DetailEventSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    interests = InterestSerializer(many=True)
    banners = EventBannerSerializer(many=True)
    organizer = OrganizerSerializer(read_only=True)
    event_dates = EventDateSerializer(many=True, source='permanentevent.dates')
    event_weeks = EventWeekSerializer(many=True, source='permanentevent.weeks')
    event_type = serializers.SerializerMethodField(read_only=True)
    is_free = serializers.SerializerMethodField(read_only=True)
    average_time = serializers.SerializerMethodField()
    is_favourite = serializers.SerializerMethodField()

    class Meta:
        model = BaseEvent
        fields = (
            'id',
            'title',
            'description',
            'banners',
            'event_type',
            'event_weeks',
            'average_time',
            'price',
            'is_free',
            'category',
            'interests',
            'organizer',
            'address',
            'is_favourite'
        )

    def get_is_favourite(self, event):
        return event in self.context.get('request').user.baseprofile.user.favourites.all()

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
                # Изменение здесь: получаем время из связанной модели EventTime через свойство time
                start_time = datetime.combine(date.today(), week.start_time)
                end_time = datetime.combine(date.today(), week.end_time)
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
    city = CitySerializer()

    class Meta:
        model = BaseEvent
        fields = ['id', 'city']


class NextEventsOrgSerializer(serializers.ModelSerializer):
    class Meta:
        model = BaseEvent
        fields = ('id', 'title', 'description', 'price',)


class RelatedEventsByInterestSerializer(serializers.ModelSerializer):
    class Meta:
        model = BaseEvent
        fields = ('id', 'title', 'description', 'price', 'interests')
