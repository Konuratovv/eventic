# Generated by Django 5.0 on 2023-12-21 07:09

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('events', '0001_initial'),
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='BaseProfile',
            fields=[
                ('customuser_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to=settings.AUTH_USER_MODEL)),
                ('city', models.CharField(max_length=150)),
                ('profile_picture', models.ImageField(upload_to='')),
            ],
            options={
                'abstract': False,
            },
            bases=('users.customuser',),
        ),
        migrations.CreateModel(
            name='Organizer',
            fields=[
                ('customuser_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to=settings.AUTH_USER_MODEL)),
                ('title', models.CharField(max_length=255)),
                ('back_img', models.ImageField(upload_to='')),
            ],
            options={
                'abstract': False,
            },
            bases=('users.customuser',),
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('baseprofile_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='profiles.baseprofile')),
                ('description', models.TextField()),
                ('first_name', models.CharField(max_length=155)),
                ('last_name', models.CharField(max_length=255)),
                ('events', models.ManyToManyField(related_name='users', to='events.event')),
                ('favourites', models.ManyToManyField(to='events.event')),
            ],
            options={
                'abstract': False,
            },
            bases=('profiles.baseprofile',),
        ),
        migrations.CreateModel(
            name='FollowOrganizer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('following', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='followers', to='profiles.organizer')),
                ('follower', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='profiles.user')),
            ],
        ),
    ]
