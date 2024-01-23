from operator import itemgetter
from django.db.models import BooleanField, Case, When, Value

from django.contrib.sites.shortcuts import get_current_site
from rest_framework import generics, status
from rest_framework.generics import ListAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from django_filters.rest_framework import DjangoFilterBackend
from .event_filters import EventFilter, EventTypeFilter
from rest_framework.pagination import LimitOffsetPagination

from .models import BaseEvent, PermanentEvent, TemporaryEvent, Category, Interests
from .serializers import DetailEventSerializer, CategorySerializer, InterestSerializer
from apps.profiles.serializer import PermanentEventSerializer, TemporaryEventSerializer, \
    MainBaseEventSerializer, LastViewedEventReadSerializer, AllMainBaseEventSerializer

from ..profiles.models import User


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
    filter_backends = (DjangoFilterBackend,)
    filterset_class = EventFilter

    # def get_queryset(self, request, *args, **kwargs):
    #     user = User.objects.get(id=self.request.user.id)
    #     queryset = BaseEvent.objects.filter(BaseEvent__event_city=user.city)
    #     return queryset


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


class CustomPagination(PageNumberPagination):
    page_size = 15
    page_size_query_param = 'page_size'
    max_page_size = 15

        # user = user.city
        # event = BaseEvent.objects.filter(address__city=user)
        # serializer = self.get_serializer(event, many=True).data
        # return Response(serializer)


class EventTypeListAPIView(ListAPIView):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return None

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

        return self.get_paginated_response(sorted_data)
    
#Вывод всех мероприятий по типам
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


    
    
