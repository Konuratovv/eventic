from django.apps import AppConfig
from constants import weekday_mapping


class EventConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.events'
    verbose_name = 'Мероприятия'

    # def ready(self):
    #     create_weeks()
    #
    # def create_weeks(self):
    #     from .models import EventWeek
    #     for week in weekday_mapping.keys():
    #         EventWeek.objects.create(week=week)
    #
