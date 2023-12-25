from django.db import models
from apps.notification.constance import CATEGORY_CHOICES
# from apps.notification.constants import *
# from apps..constants import DESTINATION_CHOICES


class Notification(models.Model):
    name = models.CharField(max_length=255)
    category = models.CharField(choices=CATEGORY_CHOICES ,max_length=255, verbose_name = "Категория мероприятия")
    start_date = models.DateField("Дата начала")
    end_date = models.DateField("Дата окончания")
    location = models.CharField(max_length=255, verbose_name = "Место проведения")
    start_time = models.TimeField(verbose_name = "Время начала")
    end_time = models.TimeField(verbose_name = "Время окончания")
    notes = models.TextField(verbose_name = "Примечание")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Событие'
        verbose_name_plural = 'События'
