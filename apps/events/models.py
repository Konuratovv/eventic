from django.db import models

from django.contrib.auth.models import User


class Category(models.Model):
    name = models.CharField(max_length=155)

    def __str__(self):
        return f"{self.name}"


class EventDate(models.Model):
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()

    def __str__(self):
        return f"{self.start_date}, {self.end_date}"


class EventWeek(models.Model):
    week = models.CharField(max_length=150, choices=None)

    def __str__(self):
        return f"{self.week}"


class BaseEvent(models.Model):
    title = models.CharField(max_length=150)
    description = models.TextField()
    banner = models.ImageField(upload_to='media/', null=True, blank=True)
    language = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=5, decimal_places=2)
    category = models.ManyToManyField(Category)

    def __str__(self):
        return f'{self.title}'


class TemporaryEvent(BaseEvent):
    dates = models.ManyToManyField(EventDate)


class PermanentEvent(BaseEvent):
    weeks = models.ManyToManyField(EventWeek)
