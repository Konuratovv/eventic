from django.contrib import admin

from apps.invitations.models import Category, Contact, Image

# Register your models here.

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'title',
        'slug'
    ]
    prepopulated_fields = {'slug': ('title',)}

@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'name',
        'user',
        'slug',
    ]
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Image)
class ImageAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'image',
        'text_color',
    ]