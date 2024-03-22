# Generated by Django 4.2.7 on 2024-03-22 16:21

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('users', '0001_initial'),
        ('events', '0001_initial'),
        ('locations', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='BaseProfile',
            fields=[
                ('customuser_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to=settings.AUTH_USER_MODEL)),
                ('profile_picture', models.ImageField(blank=True, default='default/default_ava.png', null=True, upload_to='avatars', verbose_name='Аватарка')),
                ('city', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='locations.city')),
            ],
            options={
                'abstract': False,
            },
            bases=('users.customuser',),
        ),
        migrations.CreateModel(
            name='Organizer',
            fields=[
                ('baseprofile_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='profiles.baseprofile')),
                ('title', models.CharField(max_length=255)),
                ('back_img', models.ImageField(blank=True, default='default/background.png', null=True, upload_to='organizers_banners', verbose_name='Баннер')),
                ('description', models.TextField(blank=True, max_length=500)),
                ('followers', models.PositiveBigIntegerField(blank=True, default=0)),
            ],
            options={
                'verbose_name': 'Организатор',
                'verbose_name_plural': 'Организаторы',
            },
            bases=('profiles.baseprofile',),
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('baseprofile_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='profiles.baseprofile')),
                ('first_name', models.CharField(max_length=155)),
                ('last_name', models.CharField(max_length=255)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('events', models.ManyToManyField(blank=True, related_name='users', to='events.baseevent')),
                ('favourites', models.ManyToManyField(blank=True, to='events.baseevent')),
            ],
            options={
                'verbose_name': 'Пользователь',
                'verbose_name_plural': 'Пользователи',
            },
            bases=('profiles.baseprofile',),
        ),
        migrations.CreateModel(
            name='ViewedEvent',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('timestamp', models.DateTimeField(auto_now=True)),
                ('event', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='events.baseevent')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_views', to='profiles.user')),
            ],
            options={
                'ordering': ['-timestamp'],
            },
        ),
        migrations.AddField(
            model_name='user',
            name='last_viewed_events',
            field=models.ManyToManyField(blank=True, related_name='users', to='profiles.viewedevent'),
        ),
        migrations.CreateModel(
            name='SocialLink',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('social_link_type', models.CharField(choices=[('instagram', 'Instagram'), ('facebook', 'Facebook'), ('website', 'Website')], max_length=50)),
                ('social_link', models.URLField(max_length=50)),
                ('organizer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='social_links', to='profiles.organizer')),
            ],
            options={
                'verbose_name': 'Ссылка',
                'verbose_name_plural': 'Ссылки',
            },
        ),
        migrations.CreateModel(
            name='PhoneNumber',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('phone_number', models.CharField(max_length=30, verbose_name='Введите данные')),
                ('phone_number_type', models.CharField(blank=True, choices=[('whatsapp', 'WhatsApp'), ('telegram', 'Telegram'), ('phone number', 'Phone Number')], max_length=50)),
                ('organizer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='phone_numbers', to='profiles.organizer')),
            ],
            options={
                'verbose_name': 'Номер телефона',
                'verbose_name_plural': 'Номера телефонов',
            },
        ),
        migrations.CreateModel(
            name='OrganizerAddress',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('address', models.CharField(max_length=255)),
                ('organizer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='addresses', to='profiles.organizer')),
            ],
            options={
                'verbose_name': 'Адрес',
                'verbose_name_plural': 'Адреса',
            },
        ),
    ]
