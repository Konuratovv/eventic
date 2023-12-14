from django.db import models

from django.contrib.auth.models import User


class Category(models.Model):
    name = models.CharField(max_length=155)

    def __str__(self):
        return f"{self.name}"


class EventDay(models.Model):
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()


class Event(models.Model):
    title = models.CharField(max_length=150)
    description = models.TextField()
    banner = models.ImageField(upload_to='media/', null=True, blank=True)
    language = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=5, decimal_places=2)
    # guest = models.ManyToManyField(User, on_delete=models.CASCADE)
    category = models.ManyToManyField(Category)
    event_dates = models.ManyToManyField(EventDay)
    # address

    def __str__(self):
        return f'{self.title} '

