from django.db import models
from apps.users.models import CustomUser
# Create your models here.
class EventFavorite(models.Model):
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE
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