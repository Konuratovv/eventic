from django_filters import rest_framework as filters
from .models import BaseEvent

import datetime


class CharFilterInFilter(filters.BaseInFilter, filters.CharFilter):
    pass


class EventFilter(filters.FilterSet):
    """ Здесь происходит сама логика фильтрации по категориям, интересам, и диапазону дат """
    category = CharFilterInFilter(field_name='category__slug', lookup_expr='in')
    interests = CharFilterInFilter(field_name='interests__slug', lookup_expr='in')
    start_date = filters.DateFilter(field_name='temporaryevent__dates__start_date', lookup_expr='gte')
    end_date = filters.DateFilter(method='filter_end_date')

    class Meta:
        model = BaseEvent
        fields = ['category', 'interests', 'start_date', 'end_date']

    def filter_end_date(self, queryset, name, value):
        if value:
            adjusted_value = value + datetime.timedelta(days=1)
            return queryset.filter(**{'temporaryevent__dates__end_date__lt': adjusted_value})
        return queryset


class EventTypeFilter(filters.FilterSet):
    """ Фильрация по типу eventa """
    event_type = filters.CharFilter(method='filter_event_type')

    class Meta:
        model = BaseEvent
        fields = ['event_type']

    def filter_event_type(self, queryset, name, value):
        if value == 'temporary':
            return queryset.filter(temporaryevent__isnull=False)
        elif value == 'permanent':
            return queryset.filter(permanentevent__isnull=False)
        return queryset
