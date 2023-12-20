from datetime import datetime

from django.utils import timezone
from rest_framework import generics
from rest_framework.filters import SearchFilter
from rest_framework.response import Response

from django.db.models import Q, Prefetch

from .models import BaseEvent, TemporaryEvent, PermanentEvent
from .serializers import EventSerializer


class EventRetrieveAPIView(generics.RetrieveAPIView):
    """ Вывод Eventa по id """
    serializer_class = EventSerializer

    def get(self, request, pk):
        event = BaseEvent.objects.get(id=pk)
        serializer = EventSerializer(event)
        return Response(serializer.data)


class EventListAPIView(generics.ListAPIView):
    """
    Вывод списка эвентов.
    Фильтрация по категориям.
    Фильтрация по дате евентов работает пока условно.
    """
    serializer_class = EventSerializer

    def get_queryset(self):
        categories = self.request.query_params.get('categories', '')
        interests = self.request.query_params.get('interests', '')

        filters = (Q(permanentevent__id__gt=0) |
                   Q(temporaryevent__dates__end_date__lte=timezone.now()))

        if categories:
            category_filters = Q()
            for category in categories.split(','):
                category_filters |= Q(category__name__exact=category)
            filters &= category_filters

        if interests:
            interest_filters = Q()
            for interest in interests.split(','):
                interest_filters |= Q(interests__name__exact=interest)
            filters |= interest_filters

        return BaseEvent.objects.filter(filters).order_by('-id')


class FreeEventListAPIView(generics.ListAPIView):
    serializer_class = EventSerializer
    queryset = BaseEvent.objects.filter(price=0.0)


# class PopularEventListAPIView(generics.ListAPIView):
#     serializer_class = EventSerializer
#     queryset = Event.objects.all().order_by()

