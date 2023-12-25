from django.db import models

from django.contrib.auth.models import User


class Category(models.Model):
    name = models.CharField(max_length=155)

    def __str__(self):
        return f"{self.name}"


class Interests(models.Model):
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
    # guest = models.ManyToManyField(User, on_delete=models.CASCADE)
    category = models.ManyToManyField(Category)
    interests = models.ManyToManyField(Interests)

    objects = models.Manager()


    def __str__(self):
        return f'{self.title}'


class TemporaryEvent(BaseEvent):
    dates = models.ManyToManyField(EventDate)


class PermanentEvent(BaseEvent):
    weeks = models.ManyToManyField(EventWeek)


class EventFavorite(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='user_favorites',
        verbose_name='Пользователь'
    )
    event = models.CharField(
        max_length=155,
        verbose_name='Мероприятие'
    )


    def __str__(self) -> str:
        return f'{self.user} {self.event}'


    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранные'