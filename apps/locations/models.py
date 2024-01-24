# Ваше приложение/account/models.py
from django.db import models
from django.utils.text import slugify

from apps.base.models import GetOrNoneManager


class Country(models.Model):
    country_name = models.CharField(max_length=50, verbose_name='Страна')
    slug = models.SlugField(max_length=50)
    objects = GetOrNoneManager()

    def save(self, *args, **kwargs):
        self.slug = slugify(self.country_name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.country_name

    class Meta:
        verbose_name = 'Старна'
        verbose_name_plural = 'Страны'


class Region(models.Model):
    country = models.ForeignKey(Country, on_delete=models.CASCADE, verbose_name='Страна')
    region_name = models.CharField(max_length=50, verbose_name='Регион')
    slug = models.SlugField(max_length=50)
    objects = GetOrNoneManager()

    def save(self, *args, **kwargs):
        self.slug = slugify(self.region_name)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.region_name}"

    class Meta:
        verbose_name = 'Регион'
        verbose_name_plural = 'Регионы'


class City(models.Model):
    region = models.ForeignKey(Region, on_delete=models.CASCADE, verbose_name='Регион')
    city_name = models.CharField(max_length=50, verbose_name='Город')
    slug = models.SlugField(max_length=50)
    objects = GetOrNoneManager()

    def save(self, *args, **kwargs):
        self.slug = slugify(self.city_name)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.city_name}"

    class Meta:
        verbose_name = 'Город'
        verbose_name_plural = 'Города'


class Address(models.Model):
    city = models.ForeignKey(City, on_delete=models.CASCADE, verbose_name='Город')
    address_name = models.CharField(max_length=50, verbose_name='Адрес')
    slug = models.SlugField(max_length=50)
    objects = GetOrNoneManager()

    def save(self, *args, **kwargs):
        self.slug = slugify(self.address_name)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.address_name}"

    class Meta:
        verbose_name = 'Адрес'
        verbose_name_plural = 'Адреса'
