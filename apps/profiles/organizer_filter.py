from django.db.models import Q
from django_filters import rest_framework as filters
from .models import Organizer


class CharFilterInFilter(filters.BaseInFilter, filters.CharFilter):
    pass


class OrganizerFilter(filters.FilterSet):
    interests = CharFilterInFilter(field_name='baseevent_org__interests__slug', lookup_expr='in')

    class Meta:
        model = Organizer
        fields = ['interests']

