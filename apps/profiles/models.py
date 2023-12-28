from django.db import models

from apps.base.models import nb
from apps.events.models import BaseEvent
from apps.locations.models import City
from apps.users.models import CustomUser


class BaseProfile(CustomUser):
    city = models.ForeignKey(City, on_delete=models.SET_NULL, **nb)
    profile_picture = models.ImageField()


class User(BaseProfile):
    favourites = models.ManyToManyField('events.BaseEvent', null=True, blank=True)
    description = models.TextField(blank=True)
    first_name = models.CharField(max_length=155)
    last_name = models.CharField(max_length=255)
    events = models.ManyToManyField(BaseEvent, related_name='users', null=True, blank=True)
    last_viewed_events = models.ManyToManyField('profiles.ViewedEvent', related_name='users', null=True, blank=True)



class Organizer(BaseProfile):
    title = models.CharField(max_length=255)
    back_img = models.ImageField()

class FollowOrganizer(models.Model):
    follower = models.ForeignKey(User, related_name='following', on_delete=models.CASCADE)
    following = models.ForeignKey(Organizer, related_name='followers', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    is_followed = models.BooleanField(default=False)

    objects = models.Manager()


class ViewedEvent(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    event = models.ForeignKey(BaseEvent, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-timestamp']

    objects = models.Manager()
