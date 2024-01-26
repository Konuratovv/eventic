from django.db import models


# Create your models here.
class Category(models.Model):
    """ Категории мероприятии """
    name = models.CharField(max_length=150, verbose_name="Категория")
    slug = models.SlugField(max_length=80, verbose_name='Слаг', help_text='Заполняется автоматически')

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return f"{self.name}"


class Recipient(models.Model):
    name = models.CharField(
        max_length=50,
        verbose_name="Получатель"
    )

    class Meta:
        verbose_name = 'Получатель'
        verbose_name_plural = 'Получатели'

    def __str__(self) -> str:
        return f'{self.name}'


class Invitation(models.Model):
    recipient = models.ForeignKey(
        Recipient,
        on_delete=models.CASCADE,
        verbose_name="Получатель"
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        verbose_name="Категория"
    )
    date = models.DateTimeField(
        verbose_name="Дата и время"
    )
    address = models.CharField(
        max_length=100,
        verbose_name="Адрес"
    )
    note = models.TextField(
        verbose_name="Примечания"
    )
    sender = models.CharField(
        max_length=30,
        verbose_name="Отправитель"
    )
