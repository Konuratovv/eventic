import json
from datetime import timedelta

from decouple import config
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from apps.events.models import BaseEvent, EventDate
from celery import shared_task
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.conf import settings
from django.core.mail import send_mail
from django.utils import timezone
from django.utils.crypto import get_random_string
from apps.notifications.models import BaseNotification
from apps.profiles.models import User
from apps.users.models import CustomUser
import redis


@shared_task
def send_notification_task(message_data, user_email, notification_id):
    notification = BaseNotification.objects.get(id=notification_id)
    r = redis.Redis(host='redis', port=config('REDIS_PORT', cast=int), db=config('REDIS_DB', cast=int),
                    password=config('REDIS_PASSWORD'), username=config('REDIS_USER'))

    data_bytes = r.hgetall('user_connections')
    data = {}

    for key, value in data_bytes.items():
        decoded_key = key.decode('utf-8')
        decoded_value = value.decode('utf-8')

        data[decoded_key] = decoded_value

    for email, channel_name in data.items():
        if email == user_email:
            notification.is_sent = True
            notification.save()
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.send)(channel_name, {
                'type': 'send_notification',
                'message': message_data
            })


@shared_task
def base_notification_task(notification_ids):
    notifications = BaseNotification.objects.filter(id__in=notification_ids)
    for notification in notifications:
        if hasattr(notification, 'permanentnotification'):
            event = notification.permanentnotification.follow.event.permanent_event
            event_date = notification.permanentnotification.follow.event
            user_email = notification.permanentnotification.follow.user.email
            base_event = BaseEvent.objects.get(id=event.baseevent_ptr_id)
            event_banner = base_event.banners.filter(is_img_main=True)
            notification.save()
            receipt_time_str = notification.updated_at.strftime('%Y-%m-%d %H:%M:%S')
            perm_event = {
                'id': event.id,
                'title': event.title,
                'event_week': event_date.event_week,
                'start_time': event_date.start_time.strftime('%H:%M:%S'),
                'end_time': event_date.end_time.strftime('%H:%M:%S'),
                'event_banner': f'http://209.38.228.54:81/{str(event_banner[0].image)}'
            }
            message_data = {
                'id': notification.id,
                'perm_event': perm_event,
                'is_seen': notification.permanentnotification.is_seen,
                'receipt_time': receipt_time_str
            }
            send_notification_task.delay(message_data, user_email, notification.id)
        elif hasattr(notification, 'temporarynotification'):
            event = notification.temporarynotification.follow.event.temp
            event_date = notification.temporarynotification.follow.event
            user_email = notification.temporarynotification.follow.user.email
            base_event = BaseEvent.objects.get(id=event.baseevent_ptr_id)
            event_banner = base_event.banners.filter(is_img_main=True)
            notification.save()
            receipt_time_str = notification.updated_at.strftime('%Y-%m-%d %H:%M:%S')
            temp_event = {
                'id': event.id,
                'title': event.title,
                'event_date': event_date.date.strftime('%Y-%m-%d'),
                'start_time': event_date.start_time.strftime('%H:%M:%S'),
                'end_time': event_date.end_time.strftime('%H:%M:%S'),
                'event_banner': f'http://209.38.228.54:81/media{str(event_banner[0].image)}'
            }
            message_data = {
                'id': notification.id,
                'temp_event': temp_event,
                'is_seen': notification.temporarynotification.is_seen,
                'receipt_time': receipt_time_str
            }
            send_notification_task.delay(message_data, user_email, notification.id)


@shared_task
def general_notification_task():
    current_time = timezone.now()
    two_hours_ago = current_time - timedelta(hours=2)

    actual_notifications = BaseNotification.objects.filter(
        is_seen=False,
        is_sent=False,
        send_date__date=current_time.date(),
        send_date__time__lte=current_time.time(),
        send_date__time__gte=two_hours_ago.time()
    )
    notification_ids = list(actual_notifications.values_list('id', flat=True))
    base_notification_task.delay(notification_ids)


@shared_task
def send_notifications_history(user_id, channel_name):
    current_time = timezone.now()
    start_of_day = current_time - timedelta(
        hours=current_time.hour,
        minutes=current_time.minute,
        seconds=current_time.second
    )
    two_hours_ago = current_time - timedelta(hours=2)
    notifications_history = BaseNotification.objects.filter(
        Q(
            Q(temporarynotification__follow__user_id=user_id) | Q(permanentnotification__follow__user_id=user_id),
            send_date__date=current_time.date(),
            send_date__time__gte=start_of_day.time(),
            send_date__time__lte=two_hours_ago.time()
        )
        |
        Q(
            Q(temporarynotification__follow__user_id=user_id) | Q(permanentnotification__follow__user_id=user_id),
            send_date__date=current_time.date(),
            send_date__time__gte=two_hours_ago.time(),
            send_date__time__lte=current_time.time(),
            is_sent=True
        )
    )
    notifications_history_data = []
    for notification in notifications_history:
        if hasattr(notification, 'permanentnotification'):
            event = notification.permanentnotification.follow.event.permanent_event
            event_date = notification.permanentnotification.follow.event
            base_event = BaseEvent.objects.get(id=event.baseevent_ptr_id)
            event_banner = base_event.banners.filter(is_img_main=True)
            receipt_time_str = notification.updated_at.strftime('%Y-%m-%d %H:%M:%S')
            perm_event = {
                'id': event.id,
                'title': event.title,
                'event_week': event_date.event_week,
                'start_time': event_date.start_time.strftime('%H:%M:%S'),
                'end_time': event_date.end_time.strftime('%H:%M:%S'),
                'event_banner': f'http://209.38.228.54:81/back_media/{str(event_banner[0].image)}'
            }
            message_data = {
                'id': notification.id,
                'perm_event': perm_event,
                'is_seen': notification.permanentnotification.is_seen,
                'receipt_time': receipt_time_str
            }
            notifications_history_data.append(message_data)
        elif hasattr(notification, 'temporarynotification'):
            event = notification.temporarynotification.follow.event.temp
            event_date = notification.temporarynotification.follow.event
            base_event = BaseEvent.objects.get(id=event.baseevent_ptr_id)
            event_banner = base_event.banners.filter(is_img_main=True)
            receipt_time_str = notification.updated_at.strftime('%Y-%m-%d %H:%M:%S')
            temp_event = {
                'id': event.id,
                'title': event.title,
                'event_date': event_date.date.strftime('%Y-%m-%d'),
                'start_time': event_date.start_time.strftime('%H:%M:%S'),
                'end_time': event_date.end_time.strftime('%H:%M:%S'),
                'event_banner': f'http://209.38.228.54:81/media{str(event_banner[0].image)}'
            }
            message_data = {
                'id': notification.id,
                'temp_event': temp_event,
                'is_seen': notification.temporarynotification.is_seen,
                'receipt_time': receipt_time_str
            }
            notifications_history_data.append(message_data)
    sorted_notifications = sorted(notifications_history_data, key=lambda x: x['receipt_time'], reverse=True)
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.send)(channel_name, {
        'type': 'send_notification',
        'message': sorted_notifications
    })


# @shared_task
# def new_event_notification():
#     current_time = timezone.now()
#
#     two_hours_ago = current_time - timedelta(hours=2)
#     filtered_notifications = OrganizationNotification.objects.filter(
#         is_seen=False,
#         is_sent=False,
#         send_date__date=current_time.date(),
#         send_date__time__lte=current_time.time(),
#         send_date__time__gte=two_hours_ago.time()
#     )
#
#     for notification in filtered_notifications:
#         user_email = notification.follow.user.email
#         event = notification.event
#         is_seen = notification.is_seen
#         event_banner = event.banners.filter(is_img_main=True)
#         if hasattr(event, 'temporaryevent'):
#             for date in event.dates.all():
#                 event_temp_date = date.date
#                 event_temp_start_time = date.start_time
#                 event_temp_end_time = date.end_time
#                 receipt_time_str = current_time.strftime('%Y-%m-%d %H:%M:%S')
#
#                 temp_event = {
#                     'id': event.id,
#                     'title': event.title,
#                     'event_date': event_temp_date.strftime('%Y-%m-%d'),
#                     'start_time': event_temp_start_time.strftime('%H:%M:%S'),
#                     'end_time': event_temp_end_time.strftime('%H:%M:%S'),
#                     'event_banner': f'http://209.38.228.54:81/{str(event_banner[0].image)}'
#                 }
#
#                 message_data = {
#                     'id': notification.id,
#                     'temp_event': temp_event,
#                     'is_seen': is_seen,
#                     'receipt_time': receipt_time_str,
#                 }
#
#                 r = redis.Redis(host='localhost', port=6379, db=0)
#
#                 data_bytes = r.hgetall('user_connections')
#                 data = {}
#
#                 for key, value in data_bytes.items():
#                     decoded_key = key.decode('utf-8')
#                     decoded_value = value.decode('utf-8')
#
#                     data[decoded_key] = decoded_value
#
#                 for email, channel_name in data.items():
#                     if email == user_email:
#                         notification.is_sent = True
#                         notification.save()
#                         channel_layer = get_channel_layer()
#                         async_to_sync(channel_layer.send)(channel_name, {
#                             'type': 'send_notification',
#                             'message': message_data
#                         })
#
#         if hasattr(event, 'permanentevent'):
#             for week in event.weeks.all():
#                 event_perm_date = week.event_week
#                 event_perm_start_time = week.start_time
#                 event_perm_end_time = week.end_time
#                 receipt_time_str = current_time.strftime('%Y-%m-%d %H:%M:%S')
#
#                 perm_event = {
#                     'id': event.id,
#                     'title': event.title,
#                     'event_date': event_perm_date.strftime('%Y-%m-%d'),
#                     'start_time': event_perm_start_time.strftime('%H:%M:%S'),
#                     'end_time': event_perm_end_time.strftime('%H:%M:%S'),
#                     'event_banner': f'http://209.38.228.54:81/{str(event_banner[0].image)}'
#                 }
#
#                 message_data = {
#                     'id': notification.id,
#                     'perm_event': perm_event,
#                     'is_seen': is_seen,
#                     'receipt_time': receipt_time_str,
#                 }
#
#                 r = redis.Redis(host='localhost', port=6379, db=0)
#
#                 data_bytes = r.hgetall('user_connections')
#                 data = {}
#
#                 for key, value in data_bytes.items():
#                     decoded_key = key.decode('utf-8')
#                     decoded_value = value.decode('utf-8')
#
#                     data[decoded_key] = decoded_value
#
#                 for email, channel_name in data.items():
#                     if email == user_email:
#                         notification.is_sent = True
#                         notification.save()
#                         channel_layer = get_channel_layer()
#                         async_to_sync(channel_layer.send)(channel_name, {
#                             'type': 'send_notification',
#                             'message': message_data
#                         })


@shared_task
def cleanup_old_data_task():
    not_verified_users = User.objects.filter(is_verified=False)
    fifteen_minutes_ago = timezone.now() - timedelta(minutes=15)
    users_to_delete = not_verified_users.filter(created_at__lte=fifteen_minutes_ago)
    users_to_delete.delete()

    current_time = timezone.now()
    one_day_ago = current_time - timedelta(days=1)

    old_notifications = BaseNotification.objects.filter(send_date__lte=one_day_ago)
    for old_notification in old_notifications:
        if hasattr(old_notification, 'permanentnotification'):
            old_notification.is_seen = False
            old_notification.is_seen = False
            send_date = old_notification.send_date
            current_day_of_week = send_date.weekday()
            days_until_next_weekday = (7 - current_day_of_week) % 7
            new_date = send_date + timedelta(days=days_until_next_weekday)
            old_notification.send_date = new_date
            old_notification.save()
        elif hasattr(old_notification, 'temporarynotification'):
            followed_temp = old_notification.temporarynotification.follow
            followed_temp.delete()
            old_notification.delete()

    users = User.objects.all()
    for user in users:
        user_views = user.user_views.order_by('-timestamp')
        views_to_keep = user_views[:15]
        user.user_views.exclude(id__in=views_to_keep).delete()


@shared_task
def send_verification_mail_task(email):
    generated_code = get_random_string(6, '0123456789')
    user = CustomUser.objects.get(email=email)
    user.code = generated_code
    user.save()
    subject = 'Your verification code'
    message = f'Your verification code:\n{generated_code}\nThanks for using our application.'
    from_email = settings.EMAIL_HOST_USER
    send_mail(subject, message, from_email, [email])
