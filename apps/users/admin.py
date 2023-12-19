from django.contrib import admin
from django.contrib.auth.models import Group

from apps.profiles.models import User, Organizer

# Register your models here.

admin.site.unregister(Group)
admin.site.register(User)
admin.site.register(Organizer)