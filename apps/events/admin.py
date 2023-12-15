from django.contrib import admin
from .models import Category, TemporaryEvent, PermanentEvent, EventWeek, EventDate


@admin.register(TemporaryEvent)
class TemporaryEventAdmin(admin.ModelAdmin):
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


@admin.register(PermanentEvent)
class PermanentEventAdmin(admin.ModelAdmin):
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


admin.site.register(EventWeek)
admin.site.register(EventDate)