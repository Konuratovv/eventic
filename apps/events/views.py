from rest_framework import generics
from rest_framework.filters import SearchFilter
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.pagination import LimitOffsetPagination


from .models import Category, Interests, EventBanner, EventWeek, EventDate
from .serializers import DetailEventSerializer, CategorySerializer, InterestSerializer
from .models import BaseEvent, PermanentEvent, TemporaryEvent
from apps.profiles.serializer import MainBaseEventSerializer, AllMainBaseEventSerializer
from .event_filters import EventFilter, EventTypeFilter
from ..locations.models import Address
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
    Вывод списка эвентов.
    Фильтрация по категориям: http://127.0.0.1:8000/events/?category=yarmarka
    Фильтрация по интересам: http://127.0.0.1:8000/events/?interests=rasprodaja,nizkie_ceny
    Фильтрация по диапазону дат: http://127.0.0.1:8000/events/?start_date=2024-01-18&end_date=2024-01-19
    """
    permission_classes = [IsAuthenticated]
    queryset = BaseEvent.objects.all()
    serializer_class = DetailEventSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_class = EventFilter
    search_fields = ['title']


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


class FreeEventListAPIView(generics.ListAPIView):
    """
    Получение списка бесплатных Events,
    пример: http://127.0.0.1:8000/events/free_events_list/
    """
    permission_classes = [IsAuthenticated]
    serializer_class = DetailEventSerializer
    queryset = BaseEvent.objects.filter(price=0.0)


class EventTypeListAPIView(ListAPIView):
    permission_classes = [IsAuthenticated]

    # from faker import Faker
    # fake = Faker()
    #
    # for num in range(500):
    #     organizer = Organizer.objects.order_by('?').first()
    #     category_instance = Category.objects.order_by('?').first()
    #     interests_instance = Interests.objects.order_by('?').first()
    #     address_instance = Address.objects.order_by('?').first()
    #     generate = PermanentEvent.objects.create(title=fake.catch_phrase(), description=fake.text(),
    #                                              price=fake.random_int(min=0, max=100, step=1),
    #                                              organizer=organizer, address=address_instance)
    #     generate2 = TemporaryEvent.objects.create(title=fake.catch_phrase(), description=fake.text(),
    #                                               price=fake.random_int(min=0, max=100, step=1),
    #                                               organizer=organizer, address=address_instance)
    #     generate.category.set([category_instance])
    #     generate.interests.set([interests_instance])
    #     generate2.category.set([category_instance])
    #     generate2.interests.set([interests_instance])
    #
    #     for _ in range(10):
    #         EventBanner.objects.create(event=generate, image='image.png')
    #         EventBanner.objects.create(event=generate2, image='image.png')
    #
    #     for _ in range(10):
    #         EventWeek.objects.create(perm=generate, week=fake.name(), start_time='21:18:1',
    #                                  end_time='20:18:12', slug='sreda')
    #
    #     for _ in range(10):
    #         EventDate.objects.create(temp=generate2, start_date='2024-01-20 21:03:22',
    #                                  end_date='2024-01-20 22:03:22')

    def get_queryset(self):
        return None

    def get_events_data(self, queryset, custom_user, serializer_class, context):
        serializer_class_data = serializer_class(
            queryset,
            many=True,
            context=context
        ).data
        return serializer_class_data

    def get(self, request, *args, **kwargs):
        custom_user = User.objects.prefetch_related('favourites', 'viewedevent_set').get(id=self.request.user.id)
        data = {
            'events': [],
            'perEvents': [],
            'temEvents': [],
            'freeEvents': [],
            'paidEvents': [],
            'last_viewed_events': []
        }

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
        ).order_by('-followers')
        context = {'custom_user': custom_user, 'request': request}
        events_data = self.get_events_data(events[:15], custom_user, MainBaseEventSerializer, context)

        perEvents = events.filter(permanentevent__isnull=False)[:15]
        events_data2 = self.get_events_data(perEvents, custom_user, MainBaseEventSerializer, context)

        temEvents = events.filter(temporaryevent__isnull=False)[:15]
        events_data3 = self.get_events_data(temEvents, custom_user, MainBaseEventSerializer, context)

        freeEvents = events.filter(price=0)[:15]
        events_data4 = self.get_events_data(freeEvents, custom_user, MainBaseEventSerializer, context)

        paidEvents = events.filter(price__gt=0)[:15]
        events_data5 = self.get_events_data(paidEvents, custom_user, MainBaseEventSerializer, context)

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
            {'type': 'paidEvents', 'events': events_data5},
            {'type': 'last_viewed_events', 'events': events_data6},
        ]

        return Response(sorted_data)


# Вывод всех мероприятий по типам
class AllEventsListAPIView(ListAPIView):
    serializer_class = AllMainBaseEventSerializer
    queryset = BaseEvent.objects.all()
    permission_classes = [IsAuthenticated]
    pagination_class = LimitOffsetPagination


class AllFreeEventsListAPIView(ListAPIView):
    queryset = BaseEvent.objects.filter(price=0)
    serializer_class = AllMainBaseEventSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = LimitOffsetPagination


class AllPaidEventsListAPIView(ListAPIView):
    queryset = BaseEvent.objects.filter(price__gt=0)
    serializer_class = AllMainBaseEventSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = LimitOffsetPagination


class AllTempEventsListAPIView(ListAPIView):
    permission_classes = [IsAuthenticated]
    queryset = TemporaryEvent.objects.all()
    serializer_class = AllMainBaseEventSerializer
    pagination_class = LimitOffsetPagination


class AllPermEventsListAPIView(ListAPIView):
    serializer_class = AllMainBaseEventSerializer
    queryset = PermanentEvent.objects.all()
    permission_classes = [IsAuthenticated]
    pagination_class = LimitOffsetPagination
