from django.db import models

from apps.base.models import nb
from apps.events.models import BaseEvent
from apps.locations.models import City, Address
from apps.users.models import CustomUser


class BaseProfile(CustomUser):
    profile_picture = models.ImageField(verbose_name="Аватарка", upload_to='avatars')


class User(BaseProfile):
    """ Если что я удалил все null=True у всех M2M полей. Улукбек """
    favourites = models.ManyToManyField('events.BaseEvent', blank=True,)
    # description = models.TextField(blank=True)
    first_name = models.CharField(max_length=155)
    last_name = models.CharField(max_length=255)
    events = models.ManyToManyField(BaseEvent, related_name='users', blank=True)
    last_viewed_events = models.ManyToManyField('profiles.ViewedEvent', related_name='users', blank=True)
    city = models.ForeignKey(City, on_delete=models.SET_NULL, **nb)

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return f"{self.email}"


class Organizer(BaseProfile):
    title = models.CharField(max_length=255)
    back_img = models.ImageField(verbose_name="Баннер", upload_to='organizers_banners', blank=True, null=True)
    address = models.ManyToManyField(Address, related_name='organizer_address')
    description = models.TextField(blank=True)
    # email = None

    class Meta:
        verbose_name = 'Организатор'
        verbose_name_plural = 'Организаторы'

    def __str__(self):
        return f"{self.title}"


class PhoneNumber(models.Model):
    organizer = models.ForeignKey(Organizer, on_delete=models.CASCADE, related_name='phone_numbers')
    phone_number = models.CharField(max_length=30)

    class Meta:
        verbose_name = 'Номер телефона'
        verbose_name_plural = 'Номера телефонов'

    def __str__(self):
        return f"{self.phone_number}"


class Email(models.Model):
    organizer = models.ForeignKey(Organizer, on_delete=models.CASCADE, related_name='emails')
    email = models.EmailField(max_length=50, blank=False)

    class Meta:
        verbose_name = 'Почта'
        verbose_name_plural = 'Почты'

    def __str__(self):
        return f"{self.email}"


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


class FollowOrganizer(models.Model):
    follower = models.ForeignKey(User, related_name='following', on_delete=models.CASCADE)
    following = models.ForeignKey(Organizer, related_name='followers', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    is_followed = models.BooleanField(default=False)
    objects = models.Manager()


class ViewedEvent(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    event = models.ForeignKey(BaseEvent, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-timestamp']

    objects = models.Manager()
