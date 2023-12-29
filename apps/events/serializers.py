from rest_framework import serializers

from .models import Category, EventDate, BaseEvent, EventWeek, Interests, EventBanner


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


class EventSerializer(serializers.ModelSerializer):
    category = CategorySerializer(many=True)
    interests = InterestSerializer(many=True)
    event_dates = EventDateSerializer(many=True, source='temporaryevent.dates')
    event_weeks = EventWeekSerializer(many=True, source='permanentevent.weeks')
    banners = EventBannerSerializer(many=True)
    organizer = serializers.SerializerMethodField()

    class Meta:
        model = BaseEvent
        fields = (
            'id',
            'title',
            'description',
            'language',
            'banners',
            'price',
            'event_dates',
            'event_weeks',
            'category',
            'interests',
            'city',
            'address',
            'organizer',
        )

    def get_organizer(self, obj):
        """ Получение заголовков организаторов """
        return obj.organizer.title if obj.organizer else 'No Organizer'
    get_organizer.short_description = 'Organizer'
