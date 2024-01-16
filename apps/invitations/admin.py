from django.contrib import admin

# Register your models here.
from apps.invitations.models import Invitation, Category, Recipient

# Register your models here.
admin.site.register(Invitation)
admin.site.register(Recipient)
admin.site.register(Category)