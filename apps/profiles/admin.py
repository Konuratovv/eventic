from django.contrib import admin
from django.contrib.auth.models import Group
from apps.profiles.models import User, Organizer

# Register your models here.

admin.site.unregister(Group)


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
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
    exclude = ['code', 'groups', 'is_verified', 'is_superuser']
    list_display = [
        "id",
        'title',
        "email",
        'is_staff',
        "last_login",
        'back_img',
    ]
