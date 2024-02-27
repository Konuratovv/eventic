from django.db import models
from apps.base.models import nb
from apps.events.models import BaseEvent
from apps.locations.models import City
from apps.users.models import CustomUser


class BaseProfile(CustomUser):
    profile_picture = models.ImageField(verbose_name="Аватарка", upload_to='avatars', default='default/default_ava.png',
                                        **nb)
    city = models.ForeignKey(City, on_delete=models.SET_NULL, **nb)


class User(BaseProfile):
    favourites = models.ManyToManyField('events.BaseEvent', blank=True)
    events = models.ManyToManyField(BaseEvent, related_name='users', blank=True)
    first_name = models.CharField(max_length=155)
    last_name = models.CharField(max_length=255)
    last_viewed_events = models.ManyToManyField('ViewedEvent', related_name='users', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return f"{self.email}"


class Organizer(BaseProfile):
    title = models.CharField(max_length=255)
    back_img = models.ImageField(verbose_name="Баннер", upload_to='organizers_banners',
                                 default='default/background.png', blank=True, null=True)
    description = models.TextField(blank=True, max_length=500)
    followers = models.PositiveBigIntegerField(blank=True, default=0)

    class Meta:
        verbose_name = 'Организатор'
        verbose_name_plural = 'Организаторы'

    def __str__(self):
        return f"{self.title}"


class OrganizerAddress(models.Model):
    organizer = models.ForeignKey(Organizer, on_delete=models.CASCADE, related_name='addresses')
    address = models.CharField(max_length=255)

    class Meta:
        verbose_name = 'Адрес'
        verbose_name_plural = 'Адреса'


class PhoneNumber(models.Model):
    organizer = models.ForeignKey(Organizer, on_delete=models.CASCADE, related_name='phone_numbers')
    phone_number = models.CharField(max_length=30, verbose_name='Введите данные')
    phone_number_choices = [
        ('whatsapp', 'WhatsApp'),
        ('telegram', 'Telegram'),
        ('phone number', 'Phone Number')
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
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_views')
    event = models.ForeignKey(BaseEvent, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-timestamp']

    objects = models.Manager()
