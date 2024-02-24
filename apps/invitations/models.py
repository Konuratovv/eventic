from django.db import models


class Category(models.Model):
    title = models.CharField(max_length=30, verbose_name='Категория')
    slug = models.SlugField(max_length=30, verbose_name='Слаг')

    def __str__(self):
        return f"{self.title}"

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'


class Contact(models.Model):
    name = models.CharField(max_length=30, verbose_name='Контакт')
    user = models.ForeignKey('profiles.User', on_delete=models.CASCADE, related_name='contact_user',
                             verbose_name='Пользователь')
    slug = models.SlugField(max_length=30, verbose_name='Слаг')

    def __str__(self):
        return f"{self.name}"

    class Meta:
        verbose_name = 'Контакт'
        verbose_name_plural = 'Контакты'


class Image(models.Model):
    COLORS = (
        ('BLACK', 'Черный'),
        ('WHITE', 'Белый')
    )
    image = models.ImageField(verbose_name='Картинка', upload_to='invitaions')
    text_color = models.CharField(max_length=10, choices=COLORS, default='BLACK', verbose_name='Цвет текста')

    class Meta:
        verbose_name = 'Картинка'
        verbose_name_plural = 'Картинки'
