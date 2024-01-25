from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group
from django.forms import BaseInlineFormSet

from apps.profiles.models import User, Organizer, PhoneNumber, Email, SocialLink

admin.site.unregister(Group)


class RequiredInlineFormSet(BaseInlineFormSet):
    def _construct_form(self, i, **kwargs):
        form = super(RequiredInlineFormSet, self)._construct_form(i, **kwargs)
        form.empty_permitted = False
        return form


class EmailInline(admin.TabularInline):
    model = Email
    extra = 1
    max_num = 1
    formset = RequiredInlineFormSet


class PhoneNumberInline(admin.TabularInline):
    model = PhoneNumber
    extra = 1
    max_num = 1
    formset = RequiredInlineFormSet


class SocialLinkInline(admin.TabularInline):
    model = SocialLink
    extra = 1
    max_num = 1
    formset = RequiredInlineFormSet


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
    exclude = ['code', 'groups', 'is_superuser', 'email']
    inlines = [EmailInline, PhoneNumberInline, SocialLinkInline]
    list_display = [
        "id",
        'title',
        'is_staff',
        "last_login",
        'back_img',
    ]
