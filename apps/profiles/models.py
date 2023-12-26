from django.db import models

from apps.events.models import BaseEvent
from apps.users.models import CustomUser


class BaseProfile(CustomUser):
    city = models.CharField(max_length=150)
    profile_picture = models.ImageField()


class User(BaseProfile):
    favourites = models.ManyToManyField('events.BaseEvent')
    description = models.TextField(blank=True)
    first_name = models.CharField(max_length=155)
    last_name = models.CharField(max_length=255)
    events = models.ManyToManyField(BaseEvent, related_name='users')



class Organizer(BaseProfile):
    title = models.CharField(max_length=255)
    back_img = models.ImageField()



class FollowOrganizer(models.Model):
    follower = models.ForeignKey(User, related_name='following', on_delete=models.CASCADE)
    following = models.ForeignKey(Organizer, related_name='followers', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    is_followed = models.BooleanField(default=False)

    objects = models.Manager()
