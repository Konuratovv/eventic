from django.db import models

from apps.events.models import PermanentEvent


# class OrganizerEventNotification(models.Model):
#     event = models.ForeignKey('events.BaseEvent', on_delete=models.CASCADE)
#     is_read = models.BooleanField(default=False)
#     created_at = models.DateTimeField(auto_now_add=True)
#
#     class Meta:
#         verbose_name = 'Уведомление'
#         verbose_name_plural = 'Уведомления'

#
# class EventNotification(models.Model):
#     perm_event = models.ForeignKey(PermanentEvent, on_delete=models.CASCADE)
#     created_at = models.BooleanField(default=False)
#
# class