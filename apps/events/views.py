from rest_framework import generics
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from django_filters.rest_framework import DjangoFilterBackend

from .models import Category, Interests
from .serializers import BaseEventSerializer, DetailEventSerializer, CategorySerializer, InterestSerializer
from .models import BaseEvent, PermanentEvent, TemporaryEvent
from apps.profiles.serializer import MainBaseEventSerializer
from .event_filters import EventFilter, EventTypeFilter
from ..profiles.models import User
from ..profiles.serializer import LastViewedEventReadSerializer
from ..users.models import CustomUser


class EventCategoryListAPIView(generics.ListAPIView):
    """ Вывод списка категориев"""
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class EventInterestListAPIView(generics.ListAPIView):
    """ Вывод списка интересов """
    queryset = Interests.objects.all()
    serializer_class = InterestSerializer


class EventRetrieveAPIView(generics.RetrieveAPIView):
    """ Вывод Eventa по id 'Все поля' """
    serializer_class = BaseEventSerializer

    def get(self, request, pk):
        event = BaseEvent.objects.get(id=pk)
        serializer = BaseEventSerializer(event)
        return Response(serializer.data)


class EventDetailAPIView(generics.RetrieveAPIView):
    """
    Вывод Eventa по id
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
    Фильтрация по диапазону дат: http://127.0.0.1:8000/events/?category=yarmarka
    """
    permission_classes = [IsAuthenticated]
    queryset = BaseEvent.objects.all()
    serializer_class = DetailEventSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = EventFilter


class EventTypeFilterAPIView(generics.ListAPIView):
    """
    Здесь происходит фильтрация по типу мероприятия,
    Вывод всех постоянных: http://127.0.0.1:8000/events/type_filter/?event_type=permanent
    Вывод всех временных: http://127.0.0.1:8000/events/type_filter/?event_type=temporary
    """
    permission_classes = [IsAuthenticated]
    queryset = BaseEvent.objects.all()
    serializer_class = DetailEventSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = EventTypeFilter


class EventTypeListAPIView(ListAPIView):
    permission_classes = [IsAuthenticated]

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
        data['events'].extend(self.get_events_data(events[:15], custom_user, MainBaseEventSerializer, context))

        perEvents = events.filter(permanentevent__isnull=False)
        data['perEvents'].extend(self.get_events_data(perEvents, custom_user, MainBaseEventSerializer, context))

        temEvents = events.filter(temporaryevent__isnull=False)[:15]
        data['temEvents'].extend(self.get_events_data(temEvents, custom_user, MainBaseEventSerializer, context))

        freeEvents = events.filter(price=0)[:15]
        data['freeEvents'].extend(self.get_events_data(freeEvents, custom_user, MainBaseEventSerializer, context))

        paidEvents = events.filter(price__gt=0).order_by('-followers')[:15]
        data['paidEvents'].extend(self.get_events_data(paidEvents, custom_user, MainBaseEventSerializer, context))

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
        data['last_viewed_events'].extend(event_data_from_viewed)

        sorted_data = [
            {'type': 'events', 'events': data['events']},
            {'type': 'perEvents', 'events': data['perEvents']},
            {'type': 'temEvents', 'events': data['temEvents']},
            {'type': 'freeEvents', 'events': data['freeEvents']},
            {'type': 'paidEvents', 'events': data['paidEvents']},
            {'type': 'last_viewed_events', 'events': data['last_viewed_events']},
        ]

        return Response(sorted_data)
