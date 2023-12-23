from django.db.models.signals import post_save
from django.dispatch import receiver
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.utils import timezone

from apps.events.models import Event
from .models import  Notification

@receiver(post_save, sender=Event)
def send_post_created_notification(sender, instance, created, **kwargs):
    if created:
        Notification.objects.create(
            event=instance

        )
