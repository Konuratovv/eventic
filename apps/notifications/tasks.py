from datetime import timedelta, datetime

from django.utils.timezone import make_naive, get_current_timezone, make_aware

from apps.events.models import BaseEvent
from apps.notifications.consumers import NotificationConsumer

from celery import shared_task
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.conf import settings
from django.core.mail import send_mail
from django.utils import timezone
from django.utils.crypto import get_random_string

from apps.notifications.models import TemporaryNotification, PermanentNotification
from apps.profiles.models import User
from apps.profiles.serializer import ProfileSerializer
from apps.users.models import CustomUser
import redis

import json


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


@shared_task
def send_permanent_notification_task():
    current_time = timezone.now()

    two_hours_ago = current_time - timedelta(hours=2)
    filtered_notifications = PermanentNotification.objects.filter(
        is_seen=False,
        is_sent=False,
        send_date__date=current_time.date(),
        send_date__time__lte=current_time.time(),
        send_date__time__gte=two_hours_ago.time()
    )
    print(filtered_notifications)
    print(current_time)
    print(current_time.date())
    print(current_time.time())
    print(two_hours_ago.time())


    for notification in filtered_notifications:
        user_email = notification.follow.user.email
        is_seen = notification.is_seen
        event = notification.follow.event.permanent_event
        base_event = BaseEvent.objects.get(id=notification.follow.event.permanent_event.baseevent_ptr_id)
        event_banner = base_event.banners.filter(is_img_main=True)
        event_date = notification.follow.event
        receipt_time = current_time
        receipt_time_str = receipt_time.strftime('%Y-%m-%d %H:%M:%S')

        perm_event = {
            'id': event.id,
            'title': event.title,
            'week_day': event_date.event_week,
            'start_time': event_date.start_time.strftime('%H:%M:%S'),
            'end_time': event_date.end_time.strftime('%H:%M:%S'),
            'event_banner': f'http://209.38.228.54:81/{str(event_banner[0].image)}'
        }

        message_data = {
            'perm_event': perm_event,
            'is_seen': is_seen,
            'receipt_time': receipt_time_str,
        }

        r = redis.Redis(host='redis', port=6379, db=0)

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
def send_temporary_notification_task():
    current_time = timezone.now()

    two_hours_ago = current_time - timedelta(hours=2)
    filtered_notifications = TemporaryNotification.objects.filter(
        is_seen=False,
        is_sent=False,
        send_date__date=current_time.date(),
        send_date__time__lte=current_time.time(),
        send_date__time__gte=two_hours_ago.time()
    )
    for notification in filtered_notifications:
        user_email = notification.follow.user.email
        is_seen = notification.is_seen
        event = notification.follow.event.temp
        base_event = BaseEvent.objects.get(id=notification.follow.event.temp.baseevent_ptr_id)
        event_banner = base_event.banners.filter(is_img_main=True)
        event_date = notification.follow.event
        receipt_time = current_time
        receipt_time_str = receipt_time.strftime('%Y-%m-%d %H:%M:%S')

        temp_event = {
            'id': event.id,
            'title': event.title,
            'event_date': event_date.date.strftime('%Y-%m-%d'),
            'start_time': event_date.start_time.strftime('%H:%M:%S'),
            'end_time': event_date.end_time.strftime('%H:%M:%S'),
            'event_banner': f'http://209.38.228.54:81/{str(event_banner[0].image)}'
        }

        message_data = {
            'temp_event': temp_event,
            'is_seen': is_seen,
            'receipt_time': receipt_time_str,
        }

        r = redis.Redis(host='redis', port=6379, db=0)

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

# @shared_task
# def new_event_notification():
#