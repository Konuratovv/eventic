from django_filters import rest_framework as filters
from .models import BaseEvent


class CharFilterInFilter(filters.BaseInFilter, filters.CharFilter):
    pass


class EventFilter(filters.FilterSet):
    """ Здесь происходит фильтрация по категориям, интересам, и диапазону дат """
    category = CharFilterInFilter(field_name='category__name', lookup_expr='in')
    interests = CharFilterInFilter(field_name='interests__name', lookup_expr='in')
    date_range = filters.DateFromToRangeFilter(field_name='temporaryevent__dates__start_date')

    class Meta:
        model = BaseEvent
        fields = ['category', 'interests', 'date_range']

