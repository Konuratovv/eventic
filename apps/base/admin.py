from django.contrib import admin
from django_celery_beat.models import (ClockedSchedule, CrontabSchedule, IntervalSchedule,
                     PeriodicTask, SolarSchedule)
from django_celery_beat.admin import CrontabScheduleAdmin, ClockedScheduleAdmin, PeriodicTaskAdmin

# Register your models here.

admin.site.unregister(IntervalSchedule)
admin.site.unregister(CrontabSchedule, CrontabScheduleAdmin)
admin.site.unregister(SolarSchedule)
admin.site.unregister(ClockedSchedule, ClockedScheduleAdmin)
admin.site.unregister(PeriodicTask, PeriodicTaskAdmin)