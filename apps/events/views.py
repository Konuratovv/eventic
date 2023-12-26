from datetime import datetime

from rest_framework.viewsets import GenericViewSet
from django.utils import timezone
from rest_framework import mixins
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
    Фильтрпция по дате евентов работает пока условно.
    """
    serializer_class = EventSerializer

    def get_queryset(self):
        categories = self.request.query_params.get(
            'categories', '')
        filters = (Q(permanentevent__id__gt=0) |
                   Q(temporaryevent__dates__end_date__lte=timezone.now()))
        if categories:
            category_filters = Q()
            for category in categories.split(','):
                category_filters |= Q(category__name__exact=category)
            filters &= category_filters
        return BaseEvent.objects.filter(filters).order_by('-id')


class FreeEventListAPIView(generics.ListAPIView):
    serializer_class = EventSerializer
    queryset = BaseEvent.objects.filter(price=0.0)


# class PopularEventListAPIView(generics.ListAPIView):
#     serializer_class = EventSerializer
#     queryset = Event.objects.all().order_by()


class InterestsFilterEventAPIView(generics.ListAPIView):
    """
    Фильтрация по 1 категорию.
    Пример: http://127.0.0.1:8000/events/filter_cat/?category_name=Cat
    И по нескольким категориям через запятую.
    Пример: http://127.0.0.1:8000/events/filter_cat/?category_name=[cat, cat3]
    """
    serializer_class = EventSerializer

    def get_queryset(self):
        interests_name = self.request.query_params.get('interests_name', '')
        interests_names_list = interests_name.strip('[]').split(',')

        # Объект Q для каждой категории
        q_objects = [Q(interests__name__iexact=interest.strip()) for interest in interests_names_list]

        # Соединяем объекты Q с оператором ИЛИ
        combined_q_objects = q_objects.pop() if q_objects else Q()
        for q_object in q_objects:
            combined_q_objects |= q_object
        return BaseEvent.objects.filter(combined_q_objects)


