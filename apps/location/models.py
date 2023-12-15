
from django.db import models


class Location(models.Model):
    country = models.CharField(max_length=50)
    region = models.CharField(max_length=50)
    city = models.CharField(max_length=50)
    adress = models.CharField(max_length=50)