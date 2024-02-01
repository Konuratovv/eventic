from django.contrib import admin
from .models import Category, TemporaryEvent, PermanentEvent, EventWeek, EventDate, Interests, EventBanner, \
    Language, PermanentEventWeek


class EventBannerInline(admin.TabularInline):
    model = EventBanner
    extra = 1
    fields = ['image', 'is_img_main']


class EventDateInline(admin.TabularInline):
    model = EventDate
    extra = 1


class EventWeekInline(admin.StackedInline):
    model = EventWeek
    prepopulated_fields = {'slug': ('week',)}
    extra = 1


@admin.register(TemporaryEvent)
class TemporaryEventAdmin(admin.ModelAdmin):
    """ Временные """
    inlines = [EventBannerInline, EventDateInline]
    exclude = ['followers']

    list_display = [
        "title",
        "id",
        "description",
        "get_languages",
        "price",
        "get_categories",
        "get_interests",
        "organizer",
        "get_dates",
        'get_followers_count',
    ]
    list_filter = ('dates', 'interests', 'category', 'language')
    readonly_fields = ('followers', 'get_followers_count')

    def get_followers_count(self, obj):
        return obj.followers.count()

    get_followers_count.short_description = 'Количество подписчиков'
    def get_categories(self, obj):
        return obj.category.name if obj.category else ""
    get_categories.short_description = 'Категория'

    def get_interests(self, obj):
        return ", ".join([interest.name for interest in obj.interests.all()])
    get_interests.short_description = 'Интересы'

    def get_dates(self, obj):
        return ", ".join(
            [f"Дата: {date.date}. Время: {date.start_time} - {date.end_time}" for date in obj.dates.all()]
        ) if obj.dates.exists() else ""
    get_dates.short_description = 'Дата и время события'

    def get_languages(self, obj):
        return ", ".join([language.name for language in obj.language.all()])
    get_languages.short_description = 'Языки'


class PermanentEventWeekInline(admin.TabularInline):
    model = PermanentEventWeek
    extra = 1


@admin.register(PermanentEvent)
class PermanentEventAdmin(admin.ModelAdmin):
    """ Постоянные """
    inlines = [EventBannerInline, PermanentEventWeekInline]
    exclude = ['followers']
    list_display = [
        "title",
        "id",
        "description",
        "get_languages",
        "price",
        "get_categories",
        "get_interests",
        "organizer",
        "get_weeks",
        'get_followers_count' ,

    ]
    list_filter = ('interests', 'category', 'language')
    readonly_fields = ('followers', 'get_followers_count')

    def get_followers_count(self, obj):
        return obj.followers.count()

    get_followers_count.short_description = 'Количество подписчиков'

    def get_categories(self, obj):
        return obj.category.name if obj.category else ""
    get_categories.short_description = 'Категория'

    def get_interests(self, obj):
        return ", ".join([interest.name for interest in obj.interests.all()])
    get_interests.short_description = 'Интересы'

    def get_weeks(self, obj):
        return ", ".join([week.week for week in obj.weeks.all()]) if hasattr(obj, 'weeks') and obj.weeks.exists() else ""
    get_weeks.short_description = 'Недели'

    def get_languages(self, obj):
        return ", ".join([language.name for language in obj.language.all()])
    get_languages.short_description = 'Языки'


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "name",
        "slug",
    ]
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Interests)
class InterestsAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "name",

    ]
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Language)
class LanguageAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "name",
        "name_two",
        "short_name",
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
