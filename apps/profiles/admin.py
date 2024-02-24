from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group
from django.forms import BaseInlineFormSet

from apps.profiles.models import User, Organizer, PhoneNumber, SocialLink, OrganizerAddress

admin.site.unregister(Group)


class RequiredInlineFormSet(BaseInlineFormSet):
    def _construct_form(self, i, **kwargs):
        form = super(RequiredInlineFormSet, self)._construct_form(i, **kwargs)
        form.empty_permitted = False
        return form

    def _should_delete_form(self, form):
        if form.prefix == self.prefix + '-0':
            return False
        return super()._should_delete_form(form)


class OrganizerAddressInline(admin.TabularInline):
    model = OrganizerAddress
    extra = 1

    def get_extra(self, request, obj=None, **kwargs):
        if obj:
            return 0
        return super().get_extra(request, obj, **kwargs)


class PhoneNumberInline(admin.TabularInline):
    model = PhoneNumber
    extra = 1
    formset = RequiredInlineFormSet

    def get_extra(self, request, obj=None, **kwargs):
        if obj:
            return 0
        return super().get_extra(request, obj, **kwargs)


class SocialLinkInline(admin.TabularInline):
    model = SocialLink
    extra = 1
    formset = RequiredInlineFormSet

    def get_extra(self, request, obj=None, **kwargs):
        if obj:
            return 0
        return super().get_extra(request, obj, **kwargs)


@admin.register(User)
class UserAdmin(UserAdmin):
    ordering = []
    list_filter = []
    fieldsets = (
        (
            None,
            {
                'fields': (
                    'email',
                    'first_name',
                    'last_name',
                    'city',
                    'password',
                    'is_verified',
                )
            },
        ),
    )
    add_fieldsets = (
        (
            None,
            {
                'fields': (
                    'email',
                    'first_name',
                    'last_name',
                    'city',
                    'password1',
                    'password2',
                    'is_verified',
                )
            },
        ),
    )

    exclude = ['code', 'groups', 'is_superuser']
    list_display = [
        "id",
        'first_name',
        'last_name',
        "email",
        'is_verified',
        'city',
        'profile_picture',
    ]


@admin.register(Organizer)
class OrganizerAdmin(admin.ModelAdmin):
    exclude = ['code', 'groups', 'is_superuser', 'followers']
    inlines = [PhoneNumberInline, SocialLinkInline, OrganizerAddressInline]
    list_display = [
        "id",
        'title',
        'email',
        'is_staff',
        "last_login",
        'back_img',
        'get_followers_count'
    ]

    readonly_fields = ['get_followers_count']

    def get_followers_count(self, obj):
        return obj.followers

    get_followers_count.short_description = 'Количество подписчиков'
