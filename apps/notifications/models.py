from django.db import models


class Notification(models.Model):
    event = models.ForeignKey('events.BaseEvent', on_delete=models.CASCADE)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)


