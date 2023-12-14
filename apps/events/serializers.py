from rest_framework import serializers

from .models import Category, EventDay, Event


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = "__all__"


class EventDateSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventDay
        fields = "__all__"


class EventSerializer(serializers.ModelSerializer):
    category = CategorySerializer(many=True)
    event_dates = EventDateSerializer(many=True)

    class Meta:
        model = Event
        fields = "__all__"
