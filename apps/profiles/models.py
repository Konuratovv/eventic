from django.db import models

from apps.base.models import nb
from apps.events.models import BaseEvent
from apps.locations.models import City, Address
from apps.users.models import CustomUser


class BaseProfile(CustomUser):
    profile_picture = models.ImageField(verbose_name="Аватарка", upload_to='avatars', default='default/default_ava.png',
                                        **nb)


class User(BaseProfile):
    """ Если что я удалил все null=True у всех M2M полей. Улукбек """
    favourites = models.ManyToManyField('events.BaseEvent', blank=True)
    organizers = models.ManyToManyField('profiles.Organizer', blank=True)
    first_name = models.CharField(max_length=155)
    last_name = models.CharField(max_length=255)
    events = models.ManyToManyField(BaseEvent, related_name='users', blank=True)
    last_viewed_events = models.ManyToManyField('ViewedEvent', related_name='users', blank=True)
    city = models.ForeignKey(City, on_delete=models.SET_NULL, **nb)

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return f"{self.email}"


class Organizer(BaseProfile):
    title = models.CharField(max_length=255)
    back_img = models.ImageField(verbose_name="Баннер", upload_to='organizers_banners', blank=True, null=True)
    address = models.CharField(max_length=50, verbose_name='Адрес')
    description = models.TextField(blank=True)
    followers = models.PositiveBigIntegerField(blank=True, default=0)

    class Meta:
        verbose_name = 'Организатор'
        verbose_name_plural = 'Организаторы'

    def __str__(self):
        return f"{self.title}"


class PhoneNumber(models.Model):
    organizer = models.ForeignKey(Organizer, on_delete=models.CASCADE, related_name='phone_numbers')
    phone_number = models.CharField(max_length=30)
    phone_number_choices = [
        ('whatsapp', 'WhatsApp'),
        ('telegram', 'Telegram'),
    ]
    phone_number_type = models.CharField(max_length=50, choices=phone_number_choices, blank=True)

    class Meta:
        verbose_name = 'Номер телефона'
        verbose_name_plural = 'Номера телефонов'

    def __str__(self):
        return f"{self.phone_number}"


class SocialLink(models.Model):
    organizer = models.ForeignKey(Organizer, on_delete=models.CASCADE, related_name='social_links')
    social_link_choices = [
        ('instagram', 'Instagram'),
        ('facebook', 'Facebook'),
        ('website', 'Website')
    ]
    social_link_type = models.CharField(max_length=50, choices=social_link_choices)
    social_link = models.URLField(max_length=50)

    class Meta:
        verbose_name = 'Ссылка'
        verbose_name_plural = 'Ссылки'

    def __str__(self):
        return f"{self.social_link_type}"


class ViewedEvent(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    event = models.ForeignKey(BaseEvent, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-timestamp']

    objects = models.Manager()
