from django.utils import timezone
from rest_framework import generics
from rest_framework.response import Response

from django_filters.rest_framework import DjangoFilterBackend

from .models import BaseEvent
from .serializers import EventSerializer
from .event_filters import EventFilter
from ..profiles.models import User


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
    queryset = BaseEvent.objects.all()
    serializer_class = EventSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = EventFilter
    def gs(self):
        queryset = super().get_queryset()
        user = User.objects.get(id=self.request.user.id)
        # Примените фильтр для исключения завершившихся мероприятий
        queryset = queryset.filter(BaseEvent__event_city=user.city)
        return queryset

class FreeEventListAPIView(generics.ListAPIView):
    serializer_class = EventSerializer
    queryset = BaseEvent.objects.filter(price=0.0)

