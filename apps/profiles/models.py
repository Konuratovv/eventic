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


class Organizer(CustomUser):
    title = models.CharField(max_length=255)
    back_img = models.ImageField()
