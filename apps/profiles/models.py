from django.db import models
from apps.users.models import CustomUser
from apps.events.models import Event


class BaseProfile(CustomUser):
    city = models.CharField(max_length=150)
    profile_picture = models.ImageField()


class User(BaseProfile):
    favourites = models.ManyToManyField('events.Event')
    organizer = models.ManyToManyField('profiles.Organiser')
    description = models.TextField()
    first_name = models.CharField(max_length=155)
    last_name = models.CharField(max_length=255)


class Organiser(CustomUser):
    title = models.CharField(max_length=255)
    back_img = models.ImageField()

