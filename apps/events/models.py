from datetime import datetime, timedelta
from uuid import uuid4

import shortuuid
from django.db import models
from django.db.models import BigAutoField
from django.utils import timezone

from apps.base.models import nb, GetOrNoneManager


class Category(models.Model):
    """ Категории мероприятии """
    name = models.CharField(max_length=90, verbose_name="Категория")
    slug = models.SlugField(max_length=80, verbose_name='Слаг', help_text='Заполняется автоматически')

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return f"{self.name}"


class Interests(models.Model):
    """ Интересы мероприятии """
    name = models.CharField(max_length=70, verbose_name="Интересы")
    slug = models.SlugField(max_length=60, verbose_name='Слаг', help_text='Заполняется автоматически')

    class Meta:
        verbose_name = 'Интерес'
        verbose_name_plural = 'Интересы'

    def __str__(self):
        return f"{self.name}"


class Language(models.Model):
    """ Язык мероприятия """
    name = models.CharField(max_length=70, verbose_name="Язык")
    name_two = models.CharField(max_length=70, verbose_name="Language", null=True, blank=True,
                                help_text="Название на родном языке 'Английский > English'")
    short_name = models.CharField(max_length=20, verbose_name="Короткое название", help_text="РУС, ENG, КЫР")
    slug = models.SlugField(max_length=60, verbose_name='Слаг', help_text='Заполняется автоматически')

    class Meta:
        verbose_name = 'Язык'
        verbose_name_plural = 'Языки'

    def __str__(self):
        return f"{self.name}"


class BaseEvent(models.Model):
    """ Базовая модель мероприятии """
    title = models.CharField(max_length=60, verbose_name="Заголовок")
    description = models.TextField(verbose_name="Описание", max_length=500)
    language = models.ManyToManyField(Language, verbose_name="Язык", related_name="event_language")
    price = models.DecimalField(max_digits=7, decimal_places=2, verbose_name="Цена")
    category = models.ForeignKey(Category, verbose_name="Категория", on_delete=models.SET_NULL,
                                 null=True, blank=True, related_name="category")
    interests = models.ManyToManyField(Interests, verbose_name="Интересы", related_name="interests")
    organizer = models.ForeignKey('profiles.Organizer', on_delete=models.CASCADE,
                                  verbose_name='Организатор мероприятия', related_name='baseevent_org')
    city = models.ForeignKey('locations.City', on_delete=models.CASCADE, verbose_name='Город')
    address = models.CharField(max_length=50, verbose_name='Адрес')
    is_active = models.BooleanField(verbose_name="Мероприятие активно", default=True)
    followers = models.PositiveBigIntegerField(blank=True, default=0)

    objects = models.Manager()

    class Meta:
        verbose_name = 'Мероприятие'
        verbose_name_plural = 'Мероприятия'

    def __str__(self):
        return f'{self.title}'


class EventBanner(models.Model):
    """ Модель Баннера связана с BaseEvent """
    event = models.ForeignKey(BaseEvent, verbose_name="Баннеры", on_delete=models.CASCADE,
                              related_name="banners", null=True, blank=True)
    image = models.ImageField(verbose_name="Баннер", upload_to='banner')
    is_img_main = models.BooleanField(verbose_name="Главная картинка", default=False)

    class Meta:
        verbose_name = 'Баннер'
        verbose_name_plural = 'Баннеры'

    def __str__(self):
        return f"{self.event}"


class EventTime(models.Model):
    start_time = models.TimeField(verbose_name="Время начала события")
    end_time = models.TimeField(verbose_name="Время окончания события")
    objects = models.Manager()

    class Meta:
        verbose_name = 'Время постоянного события'
        verbose_name_plural = 'Время постоянных событий'

    def __str__(self):
        return f"{self.start_time} - {self.end_time}"


class TemporaryEvent(BaseEvent):
    """ Временное мероприятие наследуется от BaseEvent """

    class Meta:
        verbose_name = 'Временное мероприятие'
        verbose_name_plural = 'Временое мероприятия'


class EventDate(EventTime):
    """ Дата и время, временного мероприятия связана с TemporaryEvent """
    temp = models.ForeignKey(TemporaryEvent, on_delete=models.CASCADE, related_name='dates',
                             verbose_name='Выберите временное событие')
    date = models.DateField(verbose_name="Укажите дату начала события")

    objects = GetOrNoneManager()

    class Meta:
        verbose_name = 'Дата и время мероприятия'
        verbose_name_plural = 'Даты и время мероприятий'

    def __str__(self):
        return f"{self.start_time}, {self.end_time}"


class PermanentEvent(BaseEvent):
    """ Постоянное мероприятие наследуется от BaseEvent """

    class Meta:
        verbose_name = 'Постоянное мероприятие'
        verbose_name_plural = 'Постоянные мероприятия'


class PermanentEventDays(EventTime):
    week_days = (
        ('mo', 'пн'), ('tu', 'вт'),
        ('we', 'ср'), ('th', 'чт'),
        ('fr', 'пт'), ('sa', 'сб'),
        ('su', 'вс'),
    )
    permanent_event = models.ForeignKey(
        PermanentEvent,
        verbose_name='Выберите постоянное событие',
        related_name='weeks',
        on_delete=models.CASCADE
    )
    event_week = models.CharField(verbose_name='День недели', choices=week_days, max_length=2)

    class Meta:
        verbose_name = 'Время проведения мероприятии'
        verbose_name_plural = 'Время проведения мероприятий'

    def __str__(self):
        return f"{self.event_week}"
