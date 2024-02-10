from django.db import models

from apps.events.models import PermanentEvent


class OrganizerEventNotification(models.Model):
    event = models.ForeignKey('events.BaseEvent', on_delete=models.CASCADE)
    # date = models.DateField(blank=True, null=True)
    week = models.CharField(blank=True, null=True, max_length=255)
    start_time = models.TimeField(blank=True, null=True)
    end_time = models.TimeField(blank=True, null=True)
    # created_at = models.DateTimeField(auto_now_add=True)

    objects = models.Manager()

    class Meta:
        verbose_name = 'Уведомление'
        verbose_name_plural = 'Уведомления'