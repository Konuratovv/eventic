from django.db.models.signals import post_save
from django.dispatch import receiver, Signal

from apps.events.models import PermanentEvent, TemporaryEvent, EventWeek, EventTime
from .models import OrganizerEventNotification


@receiver(post_save, sender=PermanentEvent)
def send_permanent_event_notification(sender, instance, created, **kwargs):
    if created:
        perm_event = OrganizerEventNotification.objects.create(
            event=instance,
        )


@receiver(post_save, sender=EventWeek)
def update_notif(sender, instance, created, **kwargs):
    if created:
        notif = OrganizerEventNotification.objects.get(id=instance.permanent_event.id)
        for week in notif.event.permanentevent.weeks.all():
            if notif.week is None:
                notif.week = week.week
                notif.start_time = week.time.start_time
                notif.end_time = week.time.end_time
                notif.save()
            OrganizerEventNotification.objects.create(
                event=instance.permanent_event,
                week=week.week,
                start_time=week.time.start_time,
                end_time=week.time.end_time
            )


@receiver(post_save, sender=TemporaryEvent)
def send_temporary_event_notification(sender, instance, created, **kwargs):
    if created:
        for date_obj in instance.dates.all():
            OrganizerEventNotification.objects.create(
                event=instance,
                # date=date_obj.date,
                # start_time=date_obj.start_time,
                # end_time=date_obj.end_time
            )
