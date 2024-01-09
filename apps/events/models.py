from django.db import models

from apps.base.models import nb


class Category(models.Model):
    name = models.CharField(max_length=150, verbose_name="Категория")
    slug = models.SlugField(max_length=80)

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return f"{self.name}"


class Interests(models.Model):
    name = models.CharField(max_length=150, verbose_name="Интересы")
    slug = models.SlugField(max_length=80)

    class Meta:
        verbose_name = 'Интерес'
        verbose_name_plural = 'Интересы'

    def __str__(self):
        return f"{self.name}"


class BaseEvent(models.Model):
    """ Базовая модель мероприятии """
    title = models.CharField(max_length=150, verbose_name="Заголовок")
    description = models.TextField(verbose_name="Описание")
    language = models.CharField(max_length=100, verbose_name="Язык", choices=[("kg", "Кыргызский"),
                                                                              ("ru", "Русский"),
                                                                              ("eng", "Английский"),
                                                                              ("kg-ru", "Кыргызский-Русский"),
                                                                              ], default='ru')
    price = models.DecimalField(max_digits=7, decimal_places=2, verbose_name="Цена")
    category = models.ManyToManyField(Category, verbose_name="Категория", related_name="category")
    interests = models.ManyToManyField(Interests, verbose_name="Интересы", related_name="interests")
    organizer = models.ForeignKey('profiles.Organizer', on_delete=models.CASCADE, null=True, blank=True)
    address = models.ForeignKey('locations.Address', on_delete=models.CASCADE)
    objects = models.Manager()

    @property
    def city(self):
        return self.address.city

    class Meta:
        verbose_name = 'Мероприятие'
        verbose_name_plural = 'Мероприятия'

    def __str__(self):
        return f'{self.title}'


class EventBanner(models.Model):
    event = models.ForeignKey(BaseEvent, verbose_name="Баннеры", on_delete=models.CASCADE, related_name="banners", null=True, blank=True)
    image = models.ImageField(upload_to='media/banner')

    class Meta:
        verbose_name = 'Баннер'
        verbose_name_plural = 'Баннеры'

    def __str__(self):
        return f"{self.event}"


class TemporaryEvent(BaseEvent):
    """ Временное мероприятие наследуется от BaseEvent """

    class Meta:
        verbose_name = 'Временное мероприятие'
        verbose_name_plural = 'Временое мероприятия'

    # def __str__(self):
    #     return f"{self.dates}"


class PermanentEvent(BaseEvent):
    """ Постоянное мероприятие наследуется от BaseEvent """

    class Meta:
        verbose_name = 'Постоянное мероприятие'
        verbose_name_plural = 'Постоянные мероприятия'

    # def __str__(self):
    #     return f"{self.weeks}"


class EventWeek(models.Model):
    perm = models.ForeignKey(PermanentEvent, on_delete=models.CASCADE, related_name='weeks')
    week = models.CharField(max_length=150, verbose_name="Недели")
    slug = models.SlugField(max_length=80)
    start_time = models.TimeField()
    end_time = models.TimeField(**nb)

    class Meta:
        verbose_name = 'Неделя'
        verbose_name_plural = 'Недели'

    def __str__(self):
        return f"{self.week}"


class EventDate(models.Model):
    """ Дата мероприятия """
    temp = models.ForeignKey(TemporaryEvent, on_delete=models.CASCADE, related_name='dates')
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()

    class Meta:
        verbose_name = 'Дата мероприятия'
        verbose_name_plural = 'Даты мероприятии'

    def __str__(self):
        return f"{self.start_date}, {self.end_date}"
