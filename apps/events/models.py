from django.db import models

from apps.base.models import nb


class Category(models.Model):
    """ Категории мероприятии """
    name = models.CharField(max_length=150, verbose_name="Категория")
    slug = models.SlugField(max_length=80, verbose_name='Слаг', help_text='Заполняется автоматически')

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return f"{self.name}"


class Interests(models.Model):
    """ Интересы мероприятии """
    name = models.CharField(max_length=150, verbose_name="Интересы")
    slug = models.SlugField(max_length=80, verbose_name='Слаг', help_text='Заполняется автоматически')

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
                                                                              ], default='kg')
    price = models.DecimalField(max_digits=7, decimal_places=2, verbose_name="Цена")
    category = models.ManyToManyField(Category, verbose_name="Категория", related_name="category")
    interests = models.ManyToManyField(Interests, verbose_name="Интересы", related_name="interests")
    organizer = models.ForeignKey('profiles.Organizer', on_delete=models.CASCADE, null=True, blank=True,
                                  verbose_name='Организатор мероприятия', related_name='baseevent_org')
    address = models.ForeignKey('locations.Address', on_delete=models.CASCADE, verbose_name='Адрес')
    is_active = models.BooleanField(verbose_name="Мероприятие активно", default=True)
    objects = models.Manager()

    @property
    def city(self):
        """ Получаем доступ к объекту city через поле address """
        return self.address.city

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


class PermanentEvent(BaseEvent):
    """ Постоянное мероприятие наследуется от BaseEvent """

    class Meta:
        verbose_name = 'Постоянное мероприятие'
        verbose_name_plural = 'Постоянные мероприятия'


class EventWeek(models.Model):
    """ Модель недели и время события связан с PermanentEvent"""
    perm = models.ForeignKey(PermanentEvent, on_delete=models.CASCADE, related_name='weeks',
                             verbose_name='Выберите постоянное событие')
    week = models.CharField(max_length=150, verbose_name="Недели")
    slug = models.SlugField(max_length=80, verbose_name='Слаг', help_text='Заполняется автоматически')
    start_time = models.TimeField(verbose_name="Время начала мероприятия")
    end_time = models.TimeField(verbose_name="Время окончания мероприятия")

    class Meta:
        verbose_name = 'Неделя'
        verbose_name_plural = 'Недели'
        unique_together = ['perm', 'week']

    def __str__(self):
        return f"{self.week}"

    # я добавил чтобы не давало предурпждение
    objects = models.Manager()


class EventDate(models.Model):
    """ Дата и время, временного мероприятия связана с TemporaryEvent """
    temp = models.ForeignKey(TemporaryEvent, on_delete=models.CASCADE, related_name='dates',
                             verbose_name='Выберите временное событие')
    start_date = models.DateTimeField(verbose_name='Дата начала мероприятия')
    end_date = models.DateTimeField(verbose_name='Дата окончания мероприятия')

    class Meta:
        verbose_name = 'Дата и время мероприятия'
        verbose_name_plural = 'Даты и время мероприятий'

    def __str__(self):
        return f"{self.start_date}, {self.end_date}"

    # я добавил чтобы не давало предурпждение
    objects = models.Manager()
