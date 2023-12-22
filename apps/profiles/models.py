from django.db import models
from apps.users.models import CustomUser
from apps.events.models import Event


class BaseProfile(CustomUser):
    city = models.CharField(max_length=150)
    profile_picture = models.ImageField()


class User(BaseProfile):
    favourites = models.ManyToManyField(Event)
    description = models.TextField()
    first_name = models.CharField(max_length=155)
    last_name = models.CharField(max_length=255)
    events = models.ManyToManyField(Event, related_name='users')


class Organizer(BaseProfile):
    title = models.CharField(max_length=255)
    back_img = models.ImageField()


class FollowOrganizer(models.Model):
    follower = models.ForeignKey(User, on_delete=models.CASCADE)
    following = models.ForeignKey(Organizer, related_name='followers', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    objects = models.Manager()
