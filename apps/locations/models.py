# Ваше приложение/account/models.py
from django.db import models
from django.utils.text import slugify


class Country(models.Model):
    country_name = models.CharField(max_length=50)
    slug = models.SlugField(max_length=50, default="temporary_default_country")

    def save(self, *args, **kwargs):
        self.slug = slugify(self.country_name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.country_name


class Region(models.Model):
    country = models.ForeignKey(Country, on_delete=models.CASCADE)
    region_name = models.CharField(max_length=50)
    slug = models.SlugField(max_length=50, default="temporary_default_region")

    def save(self, *args, **kwargs):
        self.slug = slugify(self.region_name)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.region_name},"


class City(models.Model):
    region = models.ForeignKey(Region, on_delete=models.CASCADE)
    city_name = models.CharField(max_length=50)
    slug = models.SlugField(max_length=50, default="temporary_default_city")

    def save(self, *args, **kwargs):
        self.slug = slugify(self.city_name)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.city_name},"


class Address(models.Model):
    city = models.ForeignKey(City, on_delete=models.CASCADE)
    address_name = models.CharField(max_length=50)
    slug = models.SlugField(max_length=50, default="temporary_default_address")

    def save(self, *args, **kwargs):
        self.slug = slugify(self.address_name)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.address_name}"
