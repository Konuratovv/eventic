from rest_framework import generics
from rest_framework.response import Response

from .models import Event
from .serializers import EventSerializer

import django_filters


class EventRetrieveAPIView(generics.RetrieveAPIView):
    serializer_class = EventSerializer

    def get(self, request, pk):
        event = Event.objects.get(id=pk)
        serializer = EventSerializer(event)
        return Response(serializer.data)


class EventListApiView(generics.ListAPIView):
    serializer_class = EventSerializer
    queryset = Event.objects.all()

    def get_queryset(self):
        queryset = Event.objects.all()
        filterer = EventFilter(self.request.query_params, queryset=queryset)
        queryset = filterer.qs
        return queryset


class EventFilter(django_filters.FilterSet):
    start_date = django_filters.DateTimeFilter(field_name='event_dates__start_date', lookup_expr='gte')
    end_date = django_filters.DateTimeFilter(field_name='event_dates__end_date', lookup_expr='lte')

    class Meta:
        model = Event
        fields = ['start_date', 'end_date']
