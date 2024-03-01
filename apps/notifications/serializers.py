from rest_framework import serializers

from apps.notifications.models import BaseNotification


class PermanentNotificationSerializer(serializers.Serializer):
    class Meta:
        fields = [
            'perm_date_id',
        ]


class TemporaryNotificationSerializer(serializers.Serializer):
    class Meta:
        fields = [
            'temp_date_id'
        ]


class ViewNotificationSerializer(serializers.Serializer):
    notification_ids = serializers.ListField(child=serializers.IntegerField())

    class Meta:
        fields = ['notification_ids']
