from django.contrib import admin
from django.contrib.auth.models import Group

from apps.profiles.models import User, Organizer

# Register your models here.

admin.site.unregister(Group)
admin.site.register(User)


class OrganizerAdmin(admin.ModelAdmin):
    exclude = ['code', 'groups', 'is_verified', 'is_superuser']


admin.site.register(Organizer, OrganizerAdmin)
