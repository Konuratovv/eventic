from rest_framework import serializers


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
