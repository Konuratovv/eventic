from django.db.models import Prefetch, Q
from django.utils import timezone

from apps.events.models import BaseEvent, EventDate
from apps.profiles.models import User
from apps.profiles.serializer import MainBaseEventSerializer, LastViewedEventReadSerializer


def filtered_events(self, request):
    custom_user = User.objects.prefetch_related('favourites', 'user_views').get(id=self.request.user.id)

    current_time = timezone.now()

    filtered_dates = EventDate.objects.filter(
        Q(date__gt=current_time.date()) | Q(date__gte=current_time.date(), end_time__gt=current_time.time())
    )
    events = BaseEvent.objects.prefetch_related(
        Prefetch('temporaryevent__dates', queryset=filtered_dates),
        'permanentevent__weeks',
        'banners',
    ).select_related(
        'permanentevent',
        'temporaryevent',
    ).only(
        'title',
        'price',
        'organizer',
        'followers'
    ).filter(
        city__city_name=custom_user.city,
        is_active=True,
    )
    context = {'custom_user': custom_user, 'request': request}

    events_data = self.get_events_data(events[:15], MainBaseEventSerializer, context)

    popularEvents = events.order_by('-followers')[:15]
    events_data3 = self.get_events_data(popularEvents, MainBaseEventSerializer, context)

    perEvents = events.filter(permanentevent__isnull=False)[:15]
    events_data2 = self.get_events_data(perEvents, MainBaseEventSerializer, context)

    freeEvents = events.filter(price=0)[:15]
    events_data4 = self.get_events_data(freeEvents, MainBaseEventSerializer, context)

    user_viewed_events = custom_user.user_views.select_related(
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
        {'type': 'popularEvents', 'events': events_data3},
        {'type': 'freeEvents', 'events': events_data4},
        {'type': 'perEvents', 'events': events_data2},
        {'type': 'last_viewed_events', 'events': events_data6},
    ]
    return sorted_data
