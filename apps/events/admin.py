from django.contrib import admin
from django.forms import BaseInlineFormSet

from .models import Category, TemporaryEvent, PermanentEvent, EventDate, Interests, EventBanner, \
    Language, EventTime, PermanentEventDays


class RequiredInlineFormSet(BaseInlineFormSet):

    def _construct_form(self, i, **kwargs):
        form = super(RequiredInlineFormSet, self)._construct_form(i, **kwargs)
        form.empty_permitted = False
        return form

    def _should_delete_form(self, form):
        if form.prefix == self.prefix + '-0':
            return False
        return super()._should_delete_form(form)


class EventBannerInline(admin.TabularInline):
    model = EventBanner
    extra = 1
    fields = ['image', 'is_img_main']
    formset = RequiredInlineFormSet

    def get_extra(self, request, obj=None, **kwargs):
        if obj:
            return 0
        return super().get_extra(request, obj, **kwargs)


class EventDateInline(admin.TabularInline):
    model = EventDate
    exclude = ['is_notified', 'is_active', 'uniq_int']
    extra = 1
    formset = RequiredInlineFormSet

    def get_extra(self, request, obj=None, **kwargs):
        if obj:
            return 0
        return super().get_extra(request, obj, **kwargs)



class PermanentEventDaysInline(admin.TabularInline):
    model = PermanentEventDays
    exclude = ['is_notified']
    extra = 1
    formset = RequiredInlineFormSet

    def get_extra(self, request, obj=None, **kwargs):
        if obj:
            return 0
        return super().get_extra(request, obj, **kwargs)


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
    readonly_fields = ['get_followers_count']

    def get_followers_count(self, obj):
        return obj.followers

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


@admin.register(PermanentEvent)
class PermanentEventAdmin(admin.ModelAdmin):
    """ Постоянные """
    inlines = [EventBannerInline, PermanentEventDaysInline]
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
        'get_followers_count',

    ]
    list_filter = ('interests', 'category', 'language')
    readonly_fields = ['get_followers_count']

    def get_followers_count(self, obj):
        return obj.followers

    get_followers_count.short_description = 'Количество подписчиков'

    def get_categories(self, obj):
        return obj.category.name if obj.category else ""

    get_categories.short_description = 'Категория'

    def get_interests(self, obj):
        return ", ".join([interest.name for interest in obj.interests.all()])

    get_interests.short_description = 'Интересы'

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


@admin.register(EventDate)
class EventDateAdmin(admin.ModelAdmin):
    pass


admin.site.register(PermanentEventDays)
