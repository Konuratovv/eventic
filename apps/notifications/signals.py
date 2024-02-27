from datetime import datetime, timedelta

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone

from apps.events.models import PermanentEvent, PermanentEventDays, EventDate
from apps.notifications.models import OrganizationNotification, FollowOrg
from constants import weekday_mapping


@receiver(post_save, sender=PermanentEventDays)
def send_permanent_event_notification(sender, instance, created, **kwargs):
    if created:
        follows_org = FollowOrg.objects.filter(organizer=instance.permanent_event.organizer)
        current_date = timezone.now()
        event_week = instance.event_week
        start_time = instance.start_time

        requested_weekday_index = weekday_mapping.get(event_week)
        current_weekday_index = current_date.weekday()

        days_until_requested_weekday = (requested_weekday_index - current_weekday_index) % 7

        if days_until_requested_weekday == 0:
            my_time = datetime.strptime(str(start_time), '%H:%M:%S').time()
            send_datetime = datetime.combine(current_date, my_time)
            send_datetime -= timedelta(hours=5)

            if send_datetime >= current_date:
                send_datetime -= timedelta(hours=2)
            else:
                if send_datetime.date() != current_date.date():
                    send_datetime += timedelta(days=8)
                    send_datetime -= timedelta(hours=2)
                else:
                    send_datetime += timedelta(days=7)
                    send_datetime -= timedelta(hours=2)
        else:
            requested_date = current_date + timedelta(days=days_until_requested_weekday)
            my_time = datetime.strptime(str(start_time), '%H:%M:%S').time()
            send_datetime = datetime.combine(requested_date, my_time)
            send_datetime -= timedelta(hours=5)

            if current_date.date() == send_datetime.date():
                if send_datetime.time() >= (current_date + timedelta(hours=2)).time():
                    send_datetime += timedelta(hours=5)
                    send_datetime += timedelta(days=7)
                    send_datetime -= timedelta(hours=2)
                else:
                    send_datetime -= timedelta(hours=2)
            else:
                send_datetime -= timedelta(hours=2)

        for follow in follows_org:
            OrganizationNotification.objects.create(
                follow=follow,
                event=instance.permanent_event,
                send_date=send_datetime
            )


# @receiver(post_save, sender=EventDate)
# def send_temporary_event_notification_post_save(sender, instance, **kwargs):
#
#     follows_org = FollowOrg.objects.filter(organizer=instance.temp.organizer)
#     event_date = instance.date
#     start_time = instance.start_time
#
#     combined_datetime = datetime.combine(event_date, start_time)
#     send_datetime = combined_datetime - timedelta(hours=7)
#     send_datetime_aware = timezone.make_aware(send_datetime)
#
#     for follow in follows_org:
#         OrganizationNotification.objects.create(
#             follow=follow,
#             event=instance.temp,
#             send_date=send_datetime_aware
#         )


# @receiver(post_save, sender=EventWeek)
# def update_notif(sender, instance, created, **kwargs):
#     if created:
#         notif = OrganizerEventNotification.objects.get(id=instance.permanent_event.id)
#         for week in notif.event.permanentevent.weeks.all():
#             if notif.week is None:
#                 notif.week = week.week
#                 notif.start_time = week.time.start_time
#                 notif.end_time = week.time.end_time
#                 notif.save()
#             OrganizerEventNotification.objects.create(
#                 event=instance.permanent_event,
#                 week=week.week,
#                 start_time=week.time.start_time,
#                 end_time=week.time.end_time
#             )
#
#
# @receiver(post_save, sender=TemporaryEvent)
# def send_temporary_event_notification(sender, instance, created, **kwargs):
#     if created:
#         for date_obj in instance.dates.all():
#             OrganizerEventNotification.objects.create(
#                 event=instance,
#                 # date=date_obj.date,
#                 # start_time=date_obj.start_time,
#                 # end_time=date_obj.end_time
#             )
