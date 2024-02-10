from django.db import models


class NotificationBase(models.Model):
    user = models.ForeignKey('profiles.User', on_delete=models.CASCADE)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    send_date = models.DateTimeField()

    class Meta:
        verbose_name = 'Уведомление'
        verbose_name_plural = 'Уведомления'


class NotificationPerm(NotificationBase):
    event = models.ForeignKey('events.PermanentEventDays', on_delete=models.CASCADE)


class NotificationTemp(NotificationBase):
    event = models.ForeignKey('events.EventDate', on_delete=models.CASCADE)


class NotificationOrg(NotificationBase):
    organizer = models.ForeignKey('profiles.Organizer', on_delete=models.CASCADE)
