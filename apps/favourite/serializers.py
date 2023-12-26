from rest_framework import serializers

from .models import EventFavorite

class EventFavoriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventFavorite
        fields = ('id', 'event')