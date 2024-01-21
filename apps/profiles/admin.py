from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group
from apps.profiles.models import User, Organizer, PhoneNumber, Email, SocialLink

admin.site.unregister(Group)


class EmailInline(admin.TabularInline):
    model = Email
    extra = 1


class PhoneNumberInline(admin.TabularInline):
    model = PhoneNumber
    extra = 1


class SocialLinkInline(admin.TabularInline):
    model = SocialLink
    extra = 1


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
                    'description',
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
                    'description',
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
    exclude = ['code', 'groups', 'is_superuser']
    inlines = [EmailInline, PhoneNumberInline, SocialLinkInline]
    list_display = [
        "id",
        'title',
        "email",
        'is_staff',
        "last_login",
        'back_img',
    ]
