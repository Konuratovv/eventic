from operator import itemgetter

from django.contrib.sites.shortcuts import get_current_site
from rest_framework import generics, status
from rest_framework.generics import ListAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response

from django_filters.rest_framework import DjangoFilterBackend

from .models import BaseEvent, PermanentEvent, TemporaryEvent, Category, Interests
from .serializers import BaseEventSerializer, DetailEventSerializer, CategorySerializer, InterestSerializer
from .event_filters import EventFilter
from ..profiles.models import User, FollowOrganizer
from ..profiles.serializer import LastViewedEventReadSerializer, PermanentEventSerializer, TemporaryEventSerializer


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
    Фильтрация по категориям.
    Фильтрация по интересам.
    Фильтрация по диапазону дат.
    """
    queryset = BaseEvent.objects.all()
    serializer_class = BaseEventSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = EventFilter

    def gs(self):
        queryset = super().get_queryset()
        user = User.objects.get(id=self.request.user.id)
        queryset = queryset.filter(BaseEvent__event_city=user.city)
        return queryset


class CustomPagination(PageNumberPagination):
    page_size = 15
    page_size_query_param = 'page_size'
    max_page_size = 15


class EventTypeListAPIView(ListAPIView):
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPagination

    def get(self, request, *args, **kwargs):
        data = {
            'events': [],
            'perEvents': [],
            'temEvents': [],
            'freeEvents': [],
            'paidEvents': [],
            'last_viewed_events': []
        }

        events = BaseEvent.objects.all().order_by('id')
        if events:
            events_paginated = self.paginate_queryset(events)
            for event in events_paginated:
                serializer_data = BaseEventSerializer(event).data
                serializer_data['followers'] = event.users.count()

                if serializer_data['banner'] is not None:
                    current_site = get_current_site(request).domain
                    serializer_data['banner'] = f"{request.scheme}://{current_site}{serializer_data['banner']}"
                data['events'].append(serializer_data)

        perEvents = PermanentEvent.objects.all().order_by('id')
        if perEvents:
            per_events_paginated = self.paginate_queryset(perEvents)
            for perEvent in per_events_paginated:
                serializer_data = PermanentEventSerializer(perEvent).data
                serializer_data['followers'] = perEvent.users.count()

                if serializer_data['banner'] is not None:
                    current_site = get_current_site(request).domain
                    serializer_data['banner'] = f"{request.scheme}://{current_site}{serializer_data['banner']}"
                data['perEvents'].append(serializer_data)

        temEvents = TemporaryEvent.objects.all().order_by('id')
        if temEvents:
            tem_events_paginated = self.paginate_queryset(temEvents)
            for temEvent in tem_events_paginated:
                serializer_data = TemporaryEventSerializer(temEvent).data
                serializer_data['followers'] = temEvent.users.count()

                if serializer_data['banner'] is not None:
                    current_site = get_current_site(request).domain
                    serializer_data['banner'] = f"{request.scheme}://{current_site}{serializer_data['banner']}"
                data['temEvents'].append(serializer_data)

        freeEvents = BaseEvent.objects.filter(price=0).order_by('id')
        if freeEvents:
            free_events_paginated = self.paginate_queryset(freeEvents)
            for freeEvent in free_events_paginated:
                serializer_data = BaseEventSerializer(freeEvent).data
                serializer_data['followers'] = freeEvent.users.count()

                if serializer_data['banner'] is not None:
                    current_site = get_current_site(request).domain
                    serializer_data['banner'] = f"{request.scheme}://{current_site}{serializer_data['banner']}"
                data['freeEvents'].append(serializer_data)

        paidEvents = BaseEvent.objects.filter(price__gt=0).order_by('id')
        if paidEvents:
            paid_events_paginated = self.paginate_queryset(paidEvents)
            for paidEvent in paid_events_paginated:
                serializer_data = BaseEventSerializer(paidEvent).data
                serializer_data['followers'] = paidEvent.users.count()

                if serializer_data['banner'] is not None:
                    current_site = get_current_site(request).domain
                    serializer_data['banner'] = f"{request.scheme}://{current_site}{serializer_data['banner']}"
                data['paidEvents'].append(serializer_data)

        user = User.objects.get(id=self.request.user.id)
        user_viewed_events = user.last_viewed_events.order_by('-timestamp')
        if user_viewed_events:
            user_viewed_events_paginated = self.paginate_queryset(user_viewed_events)
            serializer_data = LastViewedEventReadSerializer(user_viewed_events_paginated, many=True).data

            for serialized_object in serializer_data:
                if serialized_object['event']['banner'] is not None:
                    current_site = get_current_site(request).domain
                    serialized_object['event'][
                        'banner'] = f"{request.scheme}://{current_site}{serialized_object['event']['banner']}"
                data['last_viewed_events'].append(serialized_object['event'])

        sorted_data = [
            {'type': 'events', 'events': sorted(data['events'], key=itemgetter('followers'), reverse=True)},
            {'type': 'perEvents', 'events': sorted(data['perEvents'], key=itemgetter('followers'), reverse=True)},
            {'type': 'temEvents', 'events': sorted(data['temEvents'], key=itemgetter('followers'), reverse=True)},
            {'type': 'freeEvents', 'events': sorted(data['freeEvents'], key=itemgetter('followers'), reverse=True)},
            {'type': 'paidEvents', 'events': sorted(data['paidEvents'], key=itemgetter('followers'), reverse=True)},
            {'type': 'last_viewed_events', 'events': data['last_viewed_events']},
        ]

        return Response(sorted_data)
