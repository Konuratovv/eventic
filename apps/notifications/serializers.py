# from datetime import datetime
#
# from rest_framework import serializers
# from .models import OrganizerEventNotification
# from ..events.models import BaseEvent, EventWeek, EventTime
# from ..events.serializers import EventDateSerializer, EventBannerSerializer
# from ..profiles.models import Organizer
#
#
# class NotificationEventTimeSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = EventTime
#         fields = '__all__'
#
#
# class NotificationPermanentEventWeeksSerializer(serializers.ModelSerializer):
#     time = NotificationEventTimeSerializer()
#
#     class Meta:
#         model = EventWeek
#         fields = '__all__'
#
#
# class NotificationsOrganizerSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Organizer
#         fields = [
#             'profile_picture',
#             'title',
#         ]
#
#
# class NotificationEventsSerializer(serializers.ModelSerializer):
#     event_dates = EventDateSerializer(many=True, source='temporaryevent.dates')
#     event_weeks = NotificationPermanentEventWeeksSerializer(many=True, source='permanentevent.weeks', read_only=True)
#     banners = EventBannerSerializer(many=True, read_only=True)
#     organizer = NotificationsOrganizerSerializer()
#
#     class Meta:
#         model = BaseEvent
#         fields = [
#             'id',
#             'title',
#             'event_dates',
#             'event_weeks',
#             'price',
#             'banners',
#             'organizer',
#         ]
#
#
# class NotificationSerializer(serializers.ModelSerializer):
#     event = NotificationEventsSerializer()
#
#     class Meta:
#         model = OrganizerEventNotification
#         fields = "__all__"
