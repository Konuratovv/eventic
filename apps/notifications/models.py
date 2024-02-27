import json

from django.core.serializers.json import DjangoJSONEncoder
from django.db import models
from django.forms import model_to_dict

from apps.base.models import BaseModel
from apps.events.models import BaseEvent


class FollowBase(BaseModel):
    user = models.ForeignKey('profiles.User', on_delete=models.CASCADE, related_name='follower')

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'


class FollowPerm(FollowBase):
    event = models.ForeignKey('events.PermanentEventDays', on_delete=models.CASCADE, related_name='perm_events')


class FollowTemp(FollowBase):
    event = models.ForeignKey('events.EventDate', on_delete=models.CASCADE, related_name='temp_events')


class FollowOrg(FollowBase):
    organizer = models.ForeignKey('profiles.Organizer', on_delete=models.CASCADE, related_name='org_events')


class BaseNotification(BaseModel):
    is_seen = models.BooleanField(default=False)
    send_date = models.DateTimeField()
    is_sent = models.BooleanField(default=False)


class PermanentNotification(BaseNotification):
    follow = models.ForeignKey(FollowPerm, on_delete=models.CASCADE, related_name='notifications')


class TemporaryNotification(BaseNotification):
    follow = models.ForeignKey(FollowTemp, on_delete=models.CASCADE, related_name='notifications')


class OrganizationNotification(BaseNotification):
    follow = models.ForeignKey(FollowOrg, on_delete=models.CASCADE, related_name='notifications')
    event = models.ForeignKey(BaseEvent, on_delete=models.CASCADE, related_name='notifications')
