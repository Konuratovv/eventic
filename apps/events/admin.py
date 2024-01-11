from django.contrib import admin
from .models import Category, TemporaryEvent, PermanentEvent, EventWeek, EventDate, Interests, BaseEvent, EventBanner


class EventBannerInline(admin.TabularInline):
    model = EventBanner
    extra = 1


class EventDateInline(admin.TabularInline):
    model = EventDate
    extra = 1


class EventWeekInline(admin.StackedInline):
    model = EventWeek
    prepopulated_fields = {'slug': ('week',)}
    extra = 1


@admin.register(TemporaryEvent)
class TemporaryEventAdmin(admin.ModelAdmin):
    list_display = [
        "title",
        "description",
        "language",
        "price",
        "get_categories",
        "get_interests",
        "organizer",
        "get_dates",
        "id",
    ]
    inlines = [EventBannerInline, EventDateInline]

    def get_categories(self, obj):
        return ", ".join([category.name for category in obj.category.all()])

    get_categories.short_description = 'Категории'

    def get_interests(self, obj):
        return ", ".join([interest.name for interest in obj.interests.all()])

    get_interests.short_description = 'Интересы'

    def get_dates(self, obj):
        return ", ".join(
            [f"{date.start_date} - {date.end_date}" for date in obj.dates.all()]) if obj.dates.exists() else ""

    get_dates.short_description = 'Дата'


@admin.register(PermanentEvent)
class PermanentEventAdmin(admin.ModelAdmin):
    inlines = [EventBannerInline, EventWeekInline]
    list_display = [
        "title",
        "description",
        "language",
        "price",
        "get_categories",
        "get_interests",
        "organizer",
        "get_weeks",
        "id",
    ]

    def get_categories(self, obj):
        return ", ".join([category.name for category in obj.category.all()])

    get_categories.short_description = 'Категории'

    def get_interests(self, obj):
        return ", ".join([interest.name for interest in obj.interests.all()])

    get_interests.short_description = 'Интересы'

    def get_weeks(self, obj):
        return ", ".join([week.week for week in obj.weeks.all()]) if obj.weeks.exists() else ""

    get_weeks.short_description = 'Недели'


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "slug",
        "id",
    ]
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Interests)
class InterestsAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "id",

    ]
    prepopulated_fields = {'slug': ('name',)}


@admin.register(EventWeek)
class EventWeekAdmin(admin.ModelAdmin):
    list_display = [
        "week",
        "slug",
    ]
    prepopulated_fields = {'slug': ('week',)}


@admin.register(EventDate)
class EventDateAdmin(admin.ModelAdmin):
    pass

