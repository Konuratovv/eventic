from django.utils import timezone
from rest_framework import generics
from rest_framework.filters import SearchFilter
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.pagination import LimitOffsetPagination
from django.db.models import Prefetch, Q, OuterRef, Exists
from .models import Category, Interests, Language, EventBanner, EventDate, EventTime, PermanentEventDays
from .serializers import DetailEventSerializer, CategorySerializer, InterestSerializer, OrganizerEventSerializer
from .models import BaseEvent, PermanentEvent, TemporaryEvent
from apps.profiles.serializer import MainBaseEventSerializer, AllMainBaseEventSerializer, AllPermanentEventSerializer
from .event_filters import EventFilter, EventTypeFilter
from .services import filtered_events
from ..locations.models import Address, Country, Region, City
from ..notifications.models import FollowOrg
from ..profiles.models import User, Organizer
from ..profiles.serializer import LastViewedEventReadSerializer
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone
from django.db.models import Min

current_date = timezone.now()

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
    queryset = BaseEvent.objects.all()
    serializer_class = DetailEventSerializer

    # lookup_field = 'pk'

    def get(self, request, pk):
        event = BaseEvent.objects.get(id=pk)
        followed_organizers = FollowOrg.objects.filter(user=self.request.user.baseprofile.user)
        org_objects_list = [follow.organizer for follow in followed_organizers]
        serializer = self.get_serializer(event, context={'followed_organizers': org_objects_list, 'request': request})
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

    def get(self, request, *args, **kwargs):
        filtered_data = self.filter_queryset(self.get_queryset()).distinct()
        followed_organizers = FollowOrg.objects.filter(user=self.request.user.baseprofile.user)
        org_objects_list = [follow.organizer for follow in followed_organizers]
        serialized_data = self.get_serializer(
            filtered_data,
            many=True,
            context={'request': request, 'followed_organizers': org_objects_list}
        ).data
        return Response(serialized_data)


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
        sorted_data = filtered_events(self, request)

        return Response(sorted_data)


class AllEventsListAPIView(ListAPIView):
    serializer_class = AllMainBaseEventSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = LimitOffsetPagination

    def get_queryset(self):
        user_city = self.request.user.baseprofile.city   

        dates = EventDate.objects.filter(
            temp__id=OuterRef('pk')
        ).select_related('eventtime_ptr', 'temp')

        queryset = TemporaryEvent.objects.filter(
            city=user_city,
            is_active=True,
        ).filter(
            Q(dates__date__gt=current_date.date()) | Q(dates__date__gte=current_date.date(), dates__end_time__gte=current_date.time())
        ).annotate(
            earliest_date=Min('dates__date'),
            has_dates=Exists(dates)
        ).filter(has_dates=True).select_related(
            'organizer',
            'baseevent_ptr',
            'category'
        ).prefetch_related(
            'banners'
        ).order_by('earliest_date')
        return queryset


class AllFreeEventsListAPIView(ListAPIView):
    serializer_class = AllMainBaseEventSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = LimitOffsetPagination

    def get_queryset(self):
        user_city = self.request.user.baseprofile.city   

        dates = EventDate.objects.filter(
            Q(date__gt=current_date.date()) | Q(date__gte=current_date.date(), end_time__gt=current_date.time()),
            temp__id=OuterRef('pk')
        )
        
        queryset = TemporaryEvent.objects.filter(
            Q(dates__date__gt=current_date.date()) | Q(dates__date__gte=current_date.date(), dates__end_time__gte=current_date.time()),
            city=user_city,
            is_active=True,
            price=0,
        ).annotate(
            earliest_date=Min('dates__date'),
            has_dates=Exists(dates)
        ).filter(has_dates=True).select_related(
            'organizer',
            'baseevent_ptr',
            'category'
        ).prefetch_related(
            'banners'
        ).order_by('earliest_date')
        return queryset


class AllPermEventsListAPIView(ListAPIView):
    serializer_class = AllPermanentEventSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = LimitOffsetPagination

    def get_queryset(self):
        user_city = self.request.user.baseprofile.user.city

        queryset = PermanentEvent.objects.select_related(
            'organizer',
            'baseevent_ptr',
            'category',
        ).prefetch_related(
            Prefetch('weeks', queryset=PermanentEventDays.objects.select_related('permanent_event')),
            'banners',
        ).filter(
            is_active=True,
            city=user_city,
        )
        return queryset


class AllPopularEventsListAPIView(ListAPIView):
    serializer_class = AllMainBaseEventSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = LimitOffsetPagination

    def get_queryset(self):
        user_city = self.request.user.baseprofile.user.city

        dates = EventDate.objects.filter(
            temp__id=OuterRef('pk')
        ).select_related('eventtime_ptr', 'temp')

        perm_queryset = BaseEvent.objects.select_related(
            'organizer',
            'baseevent_ptr',
            'category',
        ).prefetch_related(
            Prefetch('weeks', queryset=PermanentEventDays.objects.select_related('permanent_event')),
            'banners',
        ).filter(
            is_active=True,
            city=user_city,
            permanentevent__isnull=False
        )

        temp_queryset = BaseEvent.objects.filter(
            city=user_city,
            is_active=True,
        ).filter(
            Q(temporaryevent__dates__date__gt=current_date.date()) | Q(temporaryevent__dates__date__gte=current_date.date(), temporaryevent__dates__end_time__gte=current_date.time()),
            temporaryevent__isnull=False
        ).annotate(
            earliest_date=Min('temporaryevent__dates__date'),
            has_dates=Exists(dates)
        ).filter(has_dates=True).select_related(
            'organizer',
            'temporaryevent',
            'permanentevent',
            'category'
        ).prefetch_related(
            'banners'
        )

        queryset = (temp_queryset | perm_queryset).order_by('-followers')
        return queryset


class OrganizerEventsAPIView(ListAPIView):
    serializer_class = AllMainBaseEventSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = LimitOffsetPagination

    def get_queryset(self):
        user_city = self.request.user.baseprofile.user.city
        organizer_id = self.kwargs.get('pk')

        dates = EventDate.objects.filter(
            temp__id=OuterRef('pk')
        ).select_related('eventtime_ptr', 'temp')

        perm_queryset = BaseEvent.objects.select_related(
            'organizer',
            'baseevent_ptr',
            'category',
        ).prefetch_related(
            Prefetch('weeks', queryset=PermanentEventDays.objects.select_related('permanent_event')),
            'banners',
        ).filter(
            is_active=True,
            city=user_city,
            permanentevent__isnull=False,
            organizer__id=organizer_id,
        )

        temp_queryset = BaseEvent.objects.filter(
            city=user_city,
            is_active=True,
        ).filter(
            Q(temporaryevent__dates__date__gt=current_date.date()) | Q(temporaryevent__dates__date__gte=current_date.date(), temporaryevent__dates__end_time__gte=current_date.time()),
            temporaryevent__isnull=False,
            organizer__id=organizer_id,
        ).annotate(
            earliest_date=Min('temporaryevent__dates__date'),
            has_dates=Exists(dates)
        ).filter(has_dates=True).select_related(
            'organizer',
            'temporaryevent',
            'permanentevent',
            'category'
        ).prefetch_related(
            'banners'
        )

        queryset = (temp_queryset | perm_queryset).order_by('-followers')

        return queryset


class EventsByInterestsAPIView(ListAPIView):
    serializer_class = AllMainBaseEventSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = LimitOffsetPagination

    def get_queryset(self):
        user_city = self.request.user.baseprofile.user.city
        event_id = self.kwargs.get('pk')
        try:
            event = BaseEvent.objects.get(id=event_id)

            dates = EventDate.objects.filter(
                temp__id=OuterRef('pk')
            ).select_related('eventtime_ptr', 'temp')

            perm_queryset = BaseEvent.objects.select_related(
                'organizer',
                'baseevent_ptr',
                'category',
            ).prefetch_related(
                Prefetch('weeks', queryset=PermanentEventDays.objects.select_related('permanent_event')),
                'banners',
            ).filter(
                is_active=True,
                city=user_city,
                permanentevent__isnull=False,
                interests__in=event.interests.all(),
            ).exclude(pk=event_id)

            temp_queryset = BaseEvent.objects.filter(
                city=user_city,
                is_active=True,
            ).filter(
                Q(temporaryevent__dates__date__gt=current_date.date()) | Q(temporaryevent__dates__date__gte=current_date.date(), temporaryevent__dates__end_time__gte=current_date.time()),
                temporaryevent__isnull=False,
                interests__in=event.interests.all(),
            ).annotate(
                earliest_date=Min('temporaryevent__dates__date'),
                has_dates=Exists(dates)
            ).filter(has_dates=True).select_related(
                'organizer',
                'temporaryevent',
                'permanentevent',
                'category'
            ).prefetch_related(
                'banners'
            ).exclude(pk=event_id)

            queryset = (temp_queryset | perm_queryset)

            return queryset
        except ObjectDoesNotExist:
            return BaseEvent.objects.none()
