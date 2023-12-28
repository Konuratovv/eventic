from django.db import models


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


class EventWeek(models.Model):
    week = models.CharField(max_length=150, verbose_name="Недели")
    slug = models.SlugField(max_length=80)

    class Meta:
        verbose_name = 'Неделя'
        verbose_name_plural = 'Недели'

    def __str__(self):
        return f"{self.week}"


class BaseEvent(models.Model):
    """ Базовая модель мероприятии """
    title = models.CharField(max_length=150, verbose_name="Заголовок")
    description = models.TextField(verbose_name="Описание")
    banner = models.ImageField(upload_to='media/', verbose_name="Банер")
    language = models.CharField(max_length=100, verbose_name="Язык")
    price = models.DecimalField(max_digits=7, decimal_places=2, verbose_name="Цена")
    category = models.ManyToManyField(Category, verbose_name="Категория", related_name="category")
    interests = models.ManyToManyField(Interests, verbose_name="Интересы", related_name="interests", null=True, blank=True)
    organizer = models.ForeignKey('profiles.Organizer', on_delete=models.CASCADE, null=True, blank=True)
    city= models.ForeignKey('locations.City',on_delete=models.CASCADE)
    adress = models.ForeignKey('locations.Adress',on_delete=models.CASCADE)
    objects = models.Manager()

    class Meta:
        verbose_name = 'Мероприятие'
        verbose_name_plural = 'Мероприятия'

    def __str__(self):
        return f'{self.title}'


class EventDate(models.Model):
    """ Дата мероприятия """
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()

    class Meta:
        verbose_name = 'Дата мероприятия'
        verbose_name_plural = 'Даты мероприятии'

    def __str__(self):
        return f"{self.start_date}, {self.end_date}"


class TemporaryEvent(BaseEvent):
    """ Временное мероприятие наследуется от BaseEvent """
    dates = models.ManyToManyField(EventDate, verbose_name="Временное мероприятие", related_name="temporaryevent")

    class Meta:
        verbose_name = 'Временное мероприятие'
        verbose_name_plural = 'Временое мероприятия'

    def __str__(self):
        return f"{self.dates}"


class PermanentEvent(BaseEvent):
    """ Постоянное мероприятие наследуется от BaseEvent """
    weeks = models.ManyToManyField(EventWeek, verbose_name="Постоянное мероприятие", related_name="permanentevent")

    class Meta:
        verbose_name = 'Постоянное мероприятие'
        verbose_name_plural = 'Постоянные мероприятия'

    def __str__(self):
        return f"{self.weeks}"
