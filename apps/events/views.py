from datetime import datetime

from django.utils import timezone
from rest_framework import generics
from rest_framework.response import Response
from django_filters import rest_framework as filters
from django.db.models import Q, Prefetch

from .models import BaseEvent
from .serializers import EventSerializer


class EventRetrieveAPIView(generics.RetrieveAPIView):
    """ Вывод Eventa по id """
    serializer_class = EventSerializer

    def get(self, request, pk):
        event = BaseEvent.objects.get(id=pk)
        serializer = EventSerializer(event)
        return Response(serializer.data)


class CharFilterInFilter(filters.BaseInFilter, filters.CharFilter):
    pass


class FilterEvent(filters.FilterSet):
    category = CharFilterInFilter(field_name='category__name', lookup_expr='in')
    interests = CharFilterInFilter(field_name='interests__name', lookup_expr='in')
    date_range = filters.DateFromToRangeFilter(field_name='temporaryevent__dates__start_date')

    class Meta:
        model = BaseEvent
        fields = ['category', 'interests', 'date_range']


class EventListAPIView(generics.ListAPIView):
    """
    Вывод списка эвентов.
    Фильтрация по категориям.
    Фильтрация по дате евентов работает пока условно.
    """
    queryset = BaseEvent.objects.all()
    serializer_class = EventSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = FilterEvent
    print(queryset)

    # def get_queryset(self):
    # categories = self.request.query_params.get('categories', '')
    # interests = self.request.query_params.get('interests', '')
    #
    # filters = (Q(permanentevent__id__gt=0) |
    #            Q(temporaryevent__dates__end_date__lte=timezone.now()))
    # print(filters)
    #
    # if categories:
    #     category_filters = Q()
    #     for category in categories.split(','):
    #         category_filters |= Q(category__name__exact=category)
    #     filters &= category_filters
    #
    # if interests:
    #     interest_filters = Q()
    #     for interest in interests.split(','):
    #         interest_filters |= Q(interests__name__exact=interest)
    #     filters |= interest_filters
    #
    # return BaseEvent.objects.filter(filters).order_by('-id')


class FreeEventListAPIView(generics.ListAPIView):
    serializer_class = EventSerializer
    queryset = BaseEvent.objects.filter(price=0.0)

# class PopularEventListAPIView(generics.ListAPIView):
#     serializer_class = EventSerializer
#     queryset = Event.objects.all().order_by()
