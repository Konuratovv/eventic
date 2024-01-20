# Ваше приложение/account/admin.py
from django.contrib import admin
from .models import Country, Region, City, Address


class AddressInline(admin.StackedInline):
    model = Address
    extra = 1
    fk_name = 'city'  # Указываем имя ForeignKey, к которому относится этот Inline
    prepopulated_fields = {'slug': ('address_name',)}


class CityInline(admin.StackedInline):
    model = City
    extra = 1
    fk_name = 'region'  # Указываем имя ForeignKey, к которому относится этот Inline
    prepopulated_fields = {'slug': ('city_name',)}


class RegionInline(admin.StackedInline):
    model = Region
    extra = 1
    fk_name = 'country'  # Указываем имя ForeignKey, к которому относится этот Inline
    prepopulated_fields = {'slug': ('region_name',)}


class CountryAdmin(admin.ModelAdmin):
    inlines = [RegionInline]
    prepopulated_fields = {'slug': ('country_name',)}


class RegionAdmin(admin.ModelAdmin):
    inlines = [CityInline]
    prepopulated_fields = {'slug': ('region_name',)}


class CityAdmin(admin.ModelAdmin):
    inlines = [AddressInline]
    prepopulated_fields = {'slug': ('city_name',)}


class AddressAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('address_name',)}


admin.site.register(Country, CountryAdmin)
admin.site.register(Region, RegionAdmin)
admin.site.register(City, CityAdmin)
admin.site.register(Address, AddressAdmin)
