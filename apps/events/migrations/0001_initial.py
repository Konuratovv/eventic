# Generated by Django 5.0 on 2024-02-04 11:53

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('locations', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='BaseEvent',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=50, verbose_name='Заголовок')),
                ('description', models.TextField(verbose_name='Описание')),
                ('price', models.DecimalField(decimal_places=2, max_digits=7, verbose_name='Цена')),
                ('is_active', models.BooleanField(default=True, verbose_name='Мероприятие активно')),
                ('followers', models.PositiveBigIntegerField(blank=True, default=0)),
                ('address', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='locations.address', verbose_name='Адрес')),
            ],
            options={
                'verbose_name': 'Мероприятие',
                'verbose_name_plural': 'Мероприятия',
            },
        ),
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=150, verbose_name='Категория')),
                ('slug', models.SlugField(help_text='Заполняется автоматически', max_length=80, verbose_name='Слаг')),
            ],
            options={
                'verbose_name': 'Категория',
                'verbose_name_plural': 'Категории',
            },
        ),
        migrations.CreateModel(
            name='EventBanner',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(upload_to='banner', verbose_name='Баннер')),
                ('is_img_main', models.BooleanField(default=False, verbose_name='Главная картинка')),
            ],
            options={
                'verbose_name': 'Баннер',
                'verbose_name_plural': 'Баннеры',
            },
        ),
        migrations.CreateModel(
            name='EventDate',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(verbose_name='Укажите дату начала события')),
                ('start_time', models.TimeField(verbose_name='Время начала события')),
                ('end_time', models.TimeField(verbose_name='Время окончания события')),
            ],
            options={
                'verbose_name': 'Дата и время мероприятия',
                'verbose_name_plural': 'Даты и время мероприятий',
            },
        ),
        migrations.CreateModel(
            name='EventWeek',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('week', models.CharField(max_length=150, verbose_name='Недели')),
                ('slug', models.SlugField(help_text='Заполняется автоматически', max_length=80, verbose_name='Слаг')),
                ('start_time', models.TimeField(verbose_name='Время начала события')),
                ('end_time', models.TimeField(verbose_name='Время окончания события')),
            ],
            options={
                'verbose_name': 'Неделя',
                'verbose_name_plural': 'Недели',
            },
        ),
        migrations.CreateModel(
            name='Interests',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=70, verbose_name='Интересы')),
                ('slug', models.SlugField(help_text='Заполняется автоматически', max_length=60, verbose_name='Слаг')),
            ],
            options={
                'verbose_name': 'Интерес',
                'verbose_name_plural': 'Интересы',
            },
        ),
        migrations.CreateModel(
            name='Language',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=70, verbose_name='Язык')),
                ('name_two', models.CharField(blank=True, help_text="Название на родном языке 'Английский > English'", max_length=70, null=True, verbose_name='Language')),
                ('short_name', models.CharField(help_text='РУС, ENG, КЫР', max_length=20, verbose_name='Короткое название')),
                ('slug', models.SlugField(help_text='Заполняется автоматически', max_length=60, verbose_name='Слаг')),
            ],
            options={
                'verbose_name': 'Язык',
                'verbose_name_plural': 'Языки',
            },
        ),
        migrations.CreateModel(
            name='PermanentEvent',
            fields=[
                ('baseevent_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='events.baseevent')),
            ],
            options={
                'verbose_name': 'Постоянное мероприятие',
                'verbose_name_plural': 'Постоянные мероприятия',
            },
            bases=('events.baseevent',),
        ),
        migrations.CreateModel(
            name='TemporaryEvent',
            fields=[
                ('baseevent_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='events.baseevent')),
            ],
            options={
                'verbose_name': 'Временное мероприятие',
                'verbose_name_plural': 'Временое мероприятия',
            },
            bases=('events.baseevent',),
        ),
    ]
