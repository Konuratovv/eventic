# from django.db.models.signals import post_save
# from django.dispatch import receiver
#
#
# from apps.events.models import *
# from .models import Notification
#
# @receiver(post_save, sender=PermanentEvent)
# def send_post_created_notification(sender, instance, created, **kwargs):
#     if created:
#
#         Notification.objects.create(
#             event=instance
#         )
# @receiver(post_save, sender=TemporaryEvent)
# def send_post_created_notification(sender, instance, created, **kwargs):
#     if created:
#
#         Notification.objects.create(
#             event=instance
#         )
