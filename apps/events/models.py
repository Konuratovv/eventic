from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=150, verbose_name="Категория")

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return f"{self.name}"


class Interests(models.Model):
    name = models.CharField(max_length=150, verbose_name="Интересы")

    class Meta:
        verbose_name = 'Интерес'
        verbose_name_plural = 'Интересы'

    def __str__(self):
        return f"{self.name}"


class EventWeek(models.Model):
    week = models.CharField(max_length=150, verbose_name="Неделя")

    class Meta:
        verbose_name = 'Неделя'
        verbose_name_plural = 'Недели'

    def __str__(self):
        return f"{self.week}"


class BaseEvent(models.Model):
    """ Базовая модель мероприятии """
    title = models.CharField(max_length=150, verbose_name="Заголовок")
    description = models.TextField(verbose_name="Описание")
    banner = models.ImageField(upload_to='media/', verbose_name="Банер", null=True, blank=True)
    language = models.CharField(max_length=100, verbose_name="Язык")
    price = models.DecimalField(max_digits=7, decimal_places=2, verbose_name="Цена")
    # guest = models.ManyToManyField(User, on_delete=models.CASCADE)
    category = models.ManyToManyField(Category, verbose_name="Категория")
    interests = models.ManyToManyField(Interests, verbose_name="Интересы")

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
    weeks = models.ManyToManyField(EventWeek)

    class Meta:
        verbose_name = 'Постоянное мероприятие'
        verbose_name_plural = 'Постоянные мероприятия'

    def __str__(self):
        return f"{self.weeks}"
