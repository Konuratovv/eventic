from datetime import datetime

from rest_framework import generics
from rest_framework.response import Response

from django.db.models import Q

from .models import BaseEvent
from .serializers import EventSerializer


class EventRetrieveAPIView(generics.RetrieveAPIView):
    serializer_class = EventSerializer

    def get(self, request, pk):
        event = BaseEvent.objects.get(id=pk)
        serializer = EventSerializer(event)
        return Response(serializer.data)


class EventListAPIView(generics.ListAPIView):
    """В данном случае, используется фильтрация объектов BaseEvent.
    Объекты фильтруются с использованием Q объекта
    (Q-объекты предоставляют OR-логику для запросов).
    В результате фильтрации отбираются те события,
    которые либо являются постоянными (имеют permanentevent__id__gt=0),
    либо временными, но уже завершились
    (temporaryevent__dates__end_date__lte=datetime.now()). Результаты сортируются по убыванию идентификаторов."""
    serializer_class = EventSerializer
    queryset = BaseEvent.objects.filter(
        Q(permanentevent__id__gt=0) |
        Q(temporaryevent__dates__end_date__lte=datetime.now())
    ).order_by('-id')


class FreeEventListAPIView(generics.ListAPIView):
    serializer_class = EventSerializer
    queryset = BaseEvent.objects.filter(price=0.0)

# class PopularEventListAPIView(generics.ListAPIView):
#     serializer_class = EventSerializer
#     queryset = Event.objects.all().order_by()