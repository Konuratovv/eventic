from celery import shared_task
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.conf import settings
from django.core.mail import send_mail
from django.utils.crypto import get_random_string

from apps.profiles.models import User
from apps.profiles.serializer import ProfileSerializer
from apps.users.models import CustomUser
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
def send_notification_task():
    user_data = User.objects.all()
    serialized_data = ProfileSerializer(user_data, many=True).data
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        "notifications",
        {
            "type": "send_notification",
            "message": serialized_data
        }
    )
