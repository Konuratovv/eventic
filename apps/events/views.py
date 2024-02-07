from django.utils import timezone
from rest_framework import generics
from rest_framework.filters import SearchFilter
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.pagination import LimitOffsetPagination

from .models import Category, Interests, Language, EventBanner, EventWeek, EventDate
from .serializers import DetailEventSerializer, CategorySerializer, InterestSerializer, OrganizerEventSerializer
from .models import BaseEvent, PermanentEvent, TemporaryEvent
from apps.profiles.serializer import MainBaseEventSerializer, AllMainBaseEventSerializer
from .event_filters import EventFilter, EventTypeFilter
from ..locations.models import Address, Country, Region, City
from ..profiles.models import User, Organizer
from ..profiles.serializer import LastViewedEventReadSerializer


class EventCategoryListAPIView(generics.ListAPIView):
    """ Вывод списка категориев"""
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class EventInterestListAPIView(generics.ListAPIView):
    """ Вывод списка интересов """
    queryset = Interests.objects.all()
    serializer_class = InterestSerializer


class EventDetailAPIView(generics.RetrieveAPIView):
    """
    Вывод Eventa по id (Detail),
    пример: http://127.0.0.1:8000/events/id/
    """
    permission_classes = [IsAuthenticated]
    serializer_class = DetailEventSerializer

    def get(self, request, pk):
        event = BaseEvent.objects.get(id=pk)
        serializer = self.get_serializer(event)
        return Response(serializer.data)


class EventListAPIView(generics.ListAPIView):
    """
    Вывод списка активных эвентов.
    Фильтрация по категориям: http://127.0.0.1:8000/events/?category=yarmarka
    Фильтрация по интересам: http://127.0.0.1:8000/events/?interests=rasprodaja,nizkie_ceny
    Фильтрация по диапазону дат: http://127.0.0.1:8000/events/?start_date=2024-01-18&end_date=2024-01-19
    """
    permission_classes = [IsAuthenticated]
    serializer_class = DetailEventSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_class = EventFilter
    search_fields = ['title']

    def get_queryset(self):
        """ Этот метод возвращает только активные мероприятия по местоположению """
        user = self.request.user
        queryset = BaseEvent.objects.filter(is_active=True)

        if hasattr(user, 'city') and user.city:
            queryset = queryset.filter(city=user.city)
        return queryset


class EventTypeFilterAPIView(generics.ListAPIView):
    """
    Здесь происходит фильтрация по типу мероприятия,
    Вывод всех постоянных: http://127.0.0.1:8000/events/filter_event_type/?event_type=permanent
    Вывод всех временных: http://127.0.0.1:8000/events/filter_event_type/?event_type=temporary
    """
    permission_classes = [IsAuthenticated]
    queryset = BaseEvent.objects.all()
    serializer_class = DetailEventSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = EventTypeFilter


class NextEventsOrgAPIView(generics.ListAPIView):
    """ Для получения следующих событий того же организатора """
    permission_classes = [IsAuthenticated]
    serializer_class = OrganizerEventSerializer

    def get_queryset(self):
        """ Возвращает список следующих событий для организатора указанного события. """
        event_id = self.kwargs.get('pk')  # Получаем ID текущего события из URL
        event = BaseEvent.objects.get(pk=event_id)
        organizer = event.organizer  # Получаем организатора события
        now = timezone.now()

        # Фильтруем события, чтобы найти будущие временные события и постоянные события этого организатора, исключая текущее
        upcoming_temporary_events = BaseEvent.objects.filter(organizer=organizer,
                                                             temporaryevent__dates__date__gt=now,
                                                             temporaryevent__isnull=False
                                                             ).exclude(id=event_id)

        permanent_events = BaseEvent.objects.filter(organizer=organizer,
                                                    permanentevent__isnull=False
                                                    ).exclude(id=event_id)

        # Объединяем queryset'ы, убираем возможные дубликаты и ограничиваем результат
        related_events = (upcoming_temporary_events | permanent_events).distinct()[:5]

        return related_events


class RelatedEventsByInterestAPIView(generics.ListAPIView):
    """ Для получения событий, связанных по интересам """
    permission_classes = [IsAuthenticated]
    serializer_class = OrganizerEventSerializer

    def get_queryset(self):
        """Возвращает список событий, связанных по интересам с текущим событием."""
        event_id = self.kwargs.get('pk')  # Получаем ID текущего события из URL
        event = BaseEvent.objects.get(pk=event_id)
        interests = event.interests.all()  # Получаем интересы текущего события
        now = timezone.now()

        # Фильтруем события для нахождения тех, что связаны по интересам, исключая текущее событие
        related_temporary_events = BaseEvent.objects.filter(interests__in=interests,
                                                            temporaryevent__dates__date__gt=now,
                                                            temporaryevent__isnull=False
                                                            ).exclude(id=event_id)

        related_permanent_events = BaseEvent.objects.filter(interests__in=interests,
                                                            permanentevent__isnull=False
                                                            ).exclude(id=event_id)

        # Объединяем queryset'ы, убираем возможные дубликаты и ограничиваем результат
        related_events = (related_temporary_events | related_permanent_events).distinct()[:5]

        return related_events


class EventTypeListAPIView(ListAPIView):
    permission_classes = [IsAuthenticated]

    # from faker import Faker
    #
    # fake = Faker()
    # country = Country.objects.create(country_name='Kyrgyzstan', slug='kyrgyz')
    # region = Region.objects.create(country=country, region_name='Chui', slug='ghjkl')
    # city = City.objects.create(region=region, city_name='Bishkek', slug='ghj')
    # address_instance = Address.objects.create(city=city, address_name='Djal', slug='ghjk')
    # organizers = Organizer.objects.create(title=fake.catch_phrase(),
    #                                       password=fake.random_int(min=0, max=100, step=1),
    #                                       email=str(fake.catch_phrase) + '@gmail.com',
    #                                       profile_picture='99504.png'
    #                                       )
    # for num in range(40):
    #     organizer = Organizer.objects.order_by('?').first()
    #     category_instance = Category.objects.order_by('?').first()
    #     interests_instance = Interests.objects.order_by('?').first()
    #     address_instance = Address.objects.order_by('?').first()
    #     language_instance = Language.objects.order_by('?').first()
    #     generate = PermanentEvent.objects.create(title=fake.catch_phrase(), description=fake.text(),
    #                                              price=fake.random_int(min=0, max=100, step=1),
    #                                              organizer=organizer, address=address_instance,
    #                                              category=category_instance)
    #     generate2 = TemporaryEvent.objects.create(title=fake.catch_phrase(), description=fake.text(),
    #                                               price=fake.random_int(min=0, max=100, step=1),
    #                                               organizer=organizer, address=address_instance,
    #                                               category=category_instance)
    #     generate.interests.set([interests_instance])
    #     generate2.interests.set([interests_instance])
    #     generate.language.set([language_instance])
    #     generate2.language.set([language_instance])
    #
    #     # Добавляем 10 EventBanner для каждого события
    #     for _ in range(3):
    #         EventBanner.objects.create(event=generate, image='image.png')
    #         EventBanner.objects.create(event=generate2, image='image.png')
    #
    #     # Добавляем 10 EventWeek для каждого PermanentEvent
    #     for _ in range(5):
    #         EventWeek.objects.create(perm=generate, week=fake.name(), start_time='21:18:1',
    #                                  end_time='20:18:12', slug='sreda', eventtime=)
    #
    #     # Добавляем 10 EventDate для каждого TemporaryEvent
    #     for _ in range(5):
    #         EventDate.objects.create(temp=generate2, start_time='21:03:22',
    #                                  end_time='22:03:22', date='2024-01-20')

    def get_queryset(self):
        return None

    def get_events_data(self, queryset, serializer_class, context):
        serializer_class_data = serializer_class(
            queryset,
            many=True,
            context=context
        ).data
        return serializer_class_data

    def get(self, request, *args, **kwargs):
        custom_user = User.objects.prefetch_related('favourites', 'viewedevent_set').get(id=self.request.user.id)

        events = BaseEvent.objects.prefetch_related(
            'permanentevent__weeks',
            'temporaryevent__dates',
            'banners'
        ).select_related(
            'permanentevent',
            'temporaryevent',
        ).only(
            'title',
            'price',
            'organizer',
            'followers'
        ).order_by('-followers').filter(address__city__city_name=custom_user.city)
        context = {'custom_user': custom_user, 'request': request}
        events_data = self.get_events_data(events[:15], MainBaseEventSerializer, context)

        perEvents = events.filter(permanentevent__isnull=False)[:15]
        events_data2 = self.get_events_data(perEvents, MainBaseEventSerializer, context)

        temEvents = events.filter(temporaryevent__isnull=False)[:15]
        events_data3 = self.get_events_data(temEvents, MainBaseEventSerializer, context)

        freeEvents = events.filter(price=0)[:15]
        events_data4 = self.get_events_data(freeEvents, MainBaseEventSerializer, context)

        user_viewed_events = custom_user.viewedevent_set.select_related(
            'event__temporaryevent',
            'event__permanentevent'
        ).prefetch_related(
            'event__banners',
            'event__permanentevent__weeks',
            'event__temporaryevent__dates'
        ).order_by('-timestamp')[:15]
        serializer_data = LastViewedEventReadSerializer(
            user_viewed_events,
            many=True,
            context={'custom_user': custom_user, 'request': request}
        ).data
        event_data_from_viewed = [event['event'] for event in serializer_data]
        events_data6 = event_data_from_viewed

        sorted_data = [
            {'type': 'events', 'events': events_data},
            {'type': 'perEvents', 'events': events_data2},
            {'type': 'temEvents', 'events': events_data3},
            {'type': 'freeEvents', 'events': events_data4},
            {'type': 'last_viewed_events', 'events': events_data6},
        ]

        return Response(sorted_data)


class AllEventsListAPIView(ListAPIView):
    serializer_class = AllMainBaseEventSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = LimitOffsetPagination

    def get_queryset(self):
        user_city = self.request.user.baseprofile.user.city.city_name
        queryset = BaseEvent.objects.filter(
            is_active=True,
            address__city__city_name=user_city,
        ).order_by('-followers')
        return queryset


class AllFreeEventsListAPIView(ListAPIView):
    serializer_class = AllMainBaseEventSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = LimitOffsetPagination

    def get_queryset(self):
        user_city = self.request.user.baseprofile.user.city.city_name
        queryset = BaseEvent.objects.filter(
            is_active=True,
            address__city__city_name=user_city,
            price=0,
        ).order_by('-followers')
        return queryset


class AllPaidEventsListAPIView(ListAPIView):
    serializer_class = AllMainBaseEventSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = LimitOffsetPagination

    def get_queryset(self):
        user_city = self.request.user.baseprofile.user.city.city_name
        queryset = BaseEvent.objects.filter(
            is_active=True,
            address__city__city_name=user_city,
            price__gt=0,
        ).order_by('-followers')
        return queryset


class AllTempEventsListAPIView(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = AllMainBaseEventSerializer
    pagination_class = LimitOffsetPagination

    def get_queryset(self):
        user_city = self.request.user.baseprofile.user.city.city_name
        queryset = TemporaryEvent.objects.filter(
            is_active=True,
            address__city__city_name=user_city,
        ).order_by('-followers')
        return queryset


class AllPermEventsListAPIView(ListAPIView):
    serializer_class = AllMainBaseEventSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = LimitOffsetPagination

    def get_queryset(self):
        user_city = self.request.user.baseprofile.user.city.city_name
        queryset = PermanentEvent.objects.filter(
            is_active=True,
            address__city__city_name=user_city,
        ).order_by('-followers')
        return queryset
