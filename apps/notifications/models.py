from django.db import models

from apps.base.models import BaseModel


class FollowBase(BaseModel):
    user = models.ForeignKey('profiles.User', on_delete=models.CASCADE, related_name='follower')

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'


class FollowPerm(FollowBase):
    event = models.ForeignKey('events.PermanentEventDays', on_delete=models.CASCADE, related_name='perm_event')


class FollowTemp(FollowBase):
    event = models.ForeignKey('events.EventDate', on_delete=models.CASCADE, related_name='temp_event')


class FollowOrg(FollowBase):
    organizer = models.ForeignKey('profiles.Organizer', on_delete=models.CASCADE, related_name='org_event')


class Notification(BaseModel):
    follow = models.ForeignKey(FollowBase, on_delete=models.CASCADE, related_name='notification')
    is_seen = models.BooleanField(default=False)
