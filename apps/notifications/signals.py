from django.db.models.signals import post_save
from django.dispatch import receiver


from apps.events.models import BaseEvent
from .models import Notification

@receiver(post_save, sender=BaseEvent)
def send_post_created_notification(sender, instance, created, **kwargs):
    if created:

        Notification.objects.create(
            event=instance
        )


