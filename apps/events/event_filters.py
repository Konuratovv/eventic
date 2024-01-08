from django_filters import rest_framework as filters
from .models import BaseEvent


class CharFilterInFilter(filters.BaseInFilter, filters.CharFilter):
    pass


class EventFilter(filters.FilterSet):
    """ Здесь происходит сама логика фильтрации по категориям, интересам, и диапазону дат """
    category = CharFilterInFilter(field_name='category__name', lookup_expr='in')
    interests = CharFilterInFilter(field_name='interests__name', lookup_expr='in')
    date_range = filters.DateFromToRangeFilter(field_name='temporaryevent__dates__start_date')
    address = CharFilterInFilter(field_name='address__address_name', lookup_expr='in')

    class Meta:
        model = BaseEvent
        fields = ['category', 'interests', 'date_range', 'address']

class LocationFilter(filters.FilterSet):


    class Meta:
        model = BaseEvent
        fields = ['address']

