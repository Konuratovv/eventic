from rest_framework import serializers
from apps.notification.models import Notification

class NotiSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = '__all__'