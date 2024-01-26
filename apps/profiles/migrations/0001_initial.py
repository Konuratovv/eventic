# Generated by Django 5.0 on 2024-01-26 08:53

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('events', '0001_initial'),
        ('locations', '0001_initial'),
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='BaseProfile',
            fields=[
                ('customuser_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to=settings.AUTH_USER_MODEL)),
                ('profile_picture', models.ImageField(upload_to='avatars', verbose_name='Аватарка')),
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
                ('back_img', models.ImageField(blank=True, null=True, upload_to='organizers_banners', verbose_name='Баннер')),
                ('description', models.TextField(blank=True)),
                ('address', models.ManyToManyField(related_name='organizer_address', to='locations.address')),
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
                ('city', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='locations.city')),
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
                ('phone_number', models.CharField(max_length=30)),
                ('organizer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='phone_numbers', to='profiles.organizer')),
            ],
            options={
                'verbose_name': 'Номер телефона',
                'verbose_name_plural': 'Номера телефонов',
            },
        ),
        migrations.CreateModel(
            name='Email',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.EmailField(max_length=50)),
                ('organizer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='emails', to='profiles.organizer')),
            ],
            options={
                'verbose_name': 'Почта',
                'verbose_name_plural': 'Почты',
            },
        ),
        migrations.CreateModel(
            name='ViewedEvent',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('timestamp', models.DateTimeField(auto_now=True)),
                ('event', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='events.baseevent')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='profiles.user')),
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
            name='FollowOrganizer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('is_followed', models.BooleanField(default=False)),
                ('following', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='followers', to='profiles.organizer')),
                ('follower', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='following', to='profiles.user')),
            ],
        ),
    ]
