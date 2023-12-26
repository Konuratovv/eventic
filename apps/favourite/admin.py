from django.contrib import admin
from .models import EventFavorite
# Register your models here.
@admin.register(EventFavorite)
class EventFavoriteAdmin(admin.ModelAdmin):
    list_display = ('user', 'event')