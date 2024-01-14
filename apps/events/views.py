from operator import itemgetter
from django.db.models import BooleanField, Case, When, Value

from django.contrib.sites.shortcuts import get_current_site
from rest_framework import generics, status
from rest_framework.generics import ListAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response

from django_filters.rest_framework import DjangoFilterBackend

from .models import BaseEvent, PermanentEvent, TemporaryEvent, Category, Interests
from .serializers import BaseEventSerializer, DetailEventSerializer, CategorySerializer, InterestSerializer
from .models import BaseEvent, PermanentEvent, TemporaryEvent
from apps.profiles.serializer import PermanentEventSerializer, TemporaryEventSerializer, \
    MainBaseEventSerializer
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

        user_obj = User.objects.get(id=request.user.id)
        followed_events = user_obj.favourites.all().values('pk')
        events = BaseEvent.objects.annotate(
            is_favourite=Case(
                When(id__in=followed_events, then=Value(True)),
                default=Value(False),
                output_field=BooleanField()
            )
        )

        if events:
            events_paginated = self.paginate_queryset(events)
            for event in events_paginated:
                serializer_data = MainBaseEventSerializer(event).data
                serializer_data['followers'] = event.users.count()

                for banner in serializer_data['banners']:
                    if banner['image'] is not None:
                        current_site = get_current_site(request).domain
                        banner['image'] = f"{request.scheme}://{current_site}{banner['image']}"
                data['events'].append(serializer_data)

        perEvents = PermanentEvent.objects.annotate(
            is_favourite=Case(
                When(baseevent_ptr_id__in=followed_events, then=Value(True)),
                default=Value(False),
                output_field=BooleanField()
            )
        )
        if perEvents:
            per_events_paginated = self.paginate_queryset(perEvents)
            for perEvent in per_events_paginated:
                serializer_data = PermanentEventSerializer(perEvent).data
                serializer_data['followers'] = perEvent.users.count()

                for banner in serializer_data['banners']:
                    if banner['image'] is not None:
                        current_site = get_current_site(request).domain
                        banner['image'] = f"{request.scheme}://{current_site}{banner['image']}"
                data['perEvents'].append(serializer_data)

        temEvents = TemporaryEvent.objects.annotate(
            is_favourite=Case(
                When(baseevent_ptr_id__in=followed_events, then=Value(True)),
                default=Value(False),
                output_field=BooleanField()
            )
        )
        if temEvents:
            tem_events_paginated = self.paginate_queryset(temEvents)
            for temEvent in tem_events_paginated:
                serializer_data = TemporaryEventSerializer(temEvent).data
                serializer_data['followers'] = temEvent.users.count()

                for banner in serializer_data['banners']:
                    if banner['image'] is not None:
                        current_site = get_current_site(request).domain
                        banner['image'] = f"{request.scheme}://{current_site}{banner['image']}"
                data['temEvents'].append(serializer_data)

        freeEvents = BaseEvent.objects.filter(price=0).annotate(
            is_favourite=Case(
                When(id__in=followed_events, then=Value(True)),
                default=Value(False),
                output_field=BooleanField()
            )
        )
        if freeEvents:
            free_events_paginated = self.paginate_queryset(freeEvents)
            for freeEvent in free_events_paginated:
                serializer_data = MainBaseEventSerializer(freeEvent).data
                serializer_data['followers'] = freeEvent.users.count()

                for banner in serializer_data['banners']:
                    if banner['image'] is not None:
                        current_site = get_current_site(request).domain
                        banner['image'] = f"{request.scheme}://{current_site}{banner['image']}"
                data['freeEvents'].append(serializer_data)

        paidEvents = BaseEvent.objects.filter(price__gt=0).annotate(
            is_favourite=Case(
                When(id__in=followed_events, then=Value(True)),
                default=Value(False),
                output_field=BooleanField()
            )
        )
        if paidEvents:
            paid_events_paginated = self.paginate_queryset(paidEvents)
            for paidEvent in paid_events_paginated:
                serializer_data = MainBaseEventSerializer(paidEvent).data
                serializer_data['followers'] = paidEvent.users.count()

                for banner in serializer_data['banners']:
                    if banner['image'] is not None:
                        current_site = get_current_site(request).domain
                        banner['image'] = f"{request.scheme}://{current_site}{banner['image']}"
                data['paidEvents'].append(serializer_data)

        user = User.objects.get(id=self.request.user.id)
        user_viewed_events = user.last_viewed_events.order_by('-timestamp')

        if user_viewed_events:
            user_viewed_events_paginated = self.paginate_queryset(user_viewed_events)
            serializer_data = LastViewedEventReadSerializer(user_viewed_events_paginated, many=True).data

            for serialized_last_viewed in serializer_data:
                event_id = serialized_last_viewed['event']['id']
                is_followed = is_followed = any(d['pk'] == event_id for d in followed_events)
                serialized_last_viewed['event']['is_favourite'] = is_followed

                for banner in serialized_last_viewed['event']['banners']:
                    if banner['image'] is not None:
                        current_site = get_current_site(request).domain
                        banner['image'] = f"{request.scheme}://{current_site}{banner['image']}"
                data['last_viewed_events'].append(serialized_last_viewed['event'])

        sorted_data = [
            {'type': 'events', 'events': sorted(data['events'], key=itemgetter('followers'), reverse=True)},
            {'type': 'perEvents', 'events': sorted(data['perEvents'], key=itemgetter('followers'), reverse=True)},
            {'type': 'temEvents', 'events': sorted(data['temEvents'], key=itemgetter('followers'), reverse=True)},
            {'type': 'freeEvents', 'events': sorted(data['freeEvents'], key=itemgetter('followers'), reverse=True)},
            {'type': 'paidEvents', 'events': sorted(data['paidEvents'], key=itemgetter('followers'), reverse=True)},
            {'type': 'last_viewed_events', 'events': data['last_viewed_events']},
        ]

        return Response(sorted_data)
