# Ваше приложение/account/admin.py
from django.contrib import admin
from .models import Country, Region, City, Adress

class AdressInline(admin.StackedInline):
    model = Adress
    extra = 1
    fk_name = 'city'  # Указываем имя ForeignKey, к которому относится этот Inline

class CityInline(admin.StackedInline):
    model = City
    extra = 1
    fk_name = 'region'  # Указываем имя ForeignKey, к которому относится этот Inline

class RegionInline(admin.StackedInline):
    model = Region
    extra = 1
    fk_name = 'country'  # Указываем имя ForeignKey, к которому относится этот Inline

class CountryAdmin(admin.ModelAdmin):
    inlines = [RegionInline]

class RegionAdmin(admin.ModelAdmin):
    inlines = [CityInline]

class CityAdmin(admin.ModelAdmin):
    inlines = [AdressInline]

admin.site.register(Country, CountryAdmin)
admin.site.register(Region, RegionAdmin)
admin.site.register(City, CityAdmin)
admin.site.register(Adress)
