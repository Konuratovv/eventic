from django.contrib import admin
from .models import Category, EventDay, Event


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "title",
        "description",
        "banner",
        "language",
        "price",
        # "guest",
        # "category",
        # "event_dates"
    ]


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "name",
    ]


@admin.register(EventDay)
class CategoryAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "start_date",
        "end_date",
    ]
