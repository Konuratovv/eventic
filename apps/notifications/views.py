from datetime import datetime, timedelta
from django.utils import timezone
from rest_framework import status, mixins
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import GenericAPIView
from django.core.exceptions import ObjectDoesNotExist

from .models import FollowPerm, FollowTemp, PermanentNotification, TemporaryNotification, BaseNotification
from .serializers import PermanentNotificationSerializer, TemporaryNotificationSerializer, ViewNotificationSerializer
from ..events.models import EventDate, PermanentEventDays, PermanentEvent, TemporaryEvent

from constants import weekday_mapping


class PermanentNotificationAPIView(mixins.CreateModelMixin, mixins.DestroyModelMixin, GenericAPIView):
    serializer_class = PermanentNotificationSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        user = self.request.user.baseprofile.user

        perm_date = PermanentEventDays.objects.filter(id=self.request.data.get('perm_date_id')).first()
        if perm_date is None:
            return Response({'status': 'day is not found'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            event = PermanentEvent.objects.get(id=self.request.data.get('perm_event_id'))
        except ObjectDoesNotExist:
            return Response({'status': 'event is not found'}, status=status.HTTP_404_NOT_FOUND)

        if not user.events.filter(id=event.id).exists():
            user.events.add(event)
            event.followers += 1
            user.save()
            event.save()

        current_date = timezone.now()
        requested_weekday = perm_date.event_week
        requested_time = perm_date.start_time

        requested_weekday_index = weekday_mapping.get(requested_weekday)
        current_weekday_index = current_date.weekday()

        days_until_requested_weekday = (requested_weekday_index - current_weekday_index) % 7

        if days_until_requested_weekday == 0:
            my_time = datetime.strptime(str(requested_time), '%H:%M:%S').time()
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
            my_time = datetime.strptime(str(requested_time), '%H:%M:%S').time()
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

        is_follow = FollowPerm.objects.filter(event=perm_date, user=user)
        if is_follow.exists():
            return Response({'status': 'you are already followed'}, status=status.HTTP_400_BAD_REQUEST)
        print(send_datetime)
        follow_perm = FollowPerm.objects.create(user=user, event=perm_date)
        PermanentNotification.objects.create(follow=follow_perm, send_date=send_datetime)
        return Response({'status': 'success'})

    def delete(self, request, *args, **kwargs):
        user = self.request.user.baseprofile.user

        perm_date = PermanentEventDays.objects.filter(id=self.request.data.get('perm_date_id')).first()
        if perm_date is None:
            return Response({'status': 'day is not found'}, status=status.HTTP_404_NOT_FOUND)
        try:
            event = PermanentEvent.objects.get(id=self.request.data.get('perm_event_id'))
        except ObjectDoesNotExist:
            return Response({'status': 'perm event is not found'}, status=status.HTTP_404_NOT_FOUND)

        if user.events.filter(id=event.id).exists():
            user.events.remove(event)
            event.followers -= 1
            user.save()
            event.save()

        followed_perm = FollowPerm.objects.filter(event=perm_date, user=user)
        if followed_perm.exists():
            for i in followed_perm[0].notifications.all():
                i.delete()
            BaseNotification.objects.filter(id=followed_perm[0].id).delete()
            followed_perm.delete()
            return Response({'status': 'success'})
        return Response({'status': 'you are not followed'}, status=status.HTTP_400_BAD_REQUEST)


class TemporaryNotificationAPIView(mixins.CreateModelMixin, mixins.DestroyModelMixin, GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = TemporaryNotificationSerializer

    def post(self, request, *args, **kwargs):
        user = self.request.user.baseprofile.user

        temp_event_date = EventDate.objects.get_or_none(id=self.request.data.get('temp_date_id'))
        if temp_event_date is None:
            return Response({'status': 'date is not found'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            event = TemporaryEvent.objects.get(id=self.request.data.get('temp_event_id'))
        except ObjectDoesNotExist:
            return Response({'status': 'temp event is not found'}, status=status.HTTP_404_NOT_FOUND)

        if not user.events.filter(id=event.id).exists():
            user.events.add(event)
            event.followers += 1
            user.save()
            event.save()

        permDate = temp_event_date.date
        perm_start_time = temp_event_date.start_time
        combined_datetime = datetime.combine(permDate, perm_start_time)
        send_datetime = combined_datetime - timedelta(hours=7)
        send_datetime_aware = timezone.make_aware(send_datetime)

        is_follow = FollowTemp.objects.filter(event=temp_event_date, user=user)
        if is_follow.exists():
            return Response({'status': 'you are already followed'}, status=status.HTTP_400_BAD_REQUEST)

        follow_temp = FollowTemp.objects.create(event=temp_event_date, user=user)
        TemporaryNotification.objects.create(follow=follow_temp, send_date=send_datetime_aware)
        return Response({'status': 'success'})

    def delete(self, request, *args, **kwargs):
        user = self.request.user.baseprofile.user

        temp_date = EventDate.objects.filter(id=self.request.data.get('temp_date_id')).first()
        if temp_date is None:
            return Response({'status': 'day is not found'}, status=status.HTTP_404_NOT_FOUND)
        try:
            event = TemporaryEvent.objects.get(id=self.request.data.get('temp_event_id'))
        except ObjectDoesNotExist:
            return Response({'status': 'temp event is not found'}, status=status.HTTP_404_NOT_FOUND)

        if user.events.filter(id=event.id).exists():
            user.events.remove(event)
            event.followers -= 1
            user.save()
            event.save()

        followed_temp = FollowTemp.objects.filter(event=temp_date, user=user)
        if followed_temp.exists():
            for i in followed_temp[0].notifications.all():
                i.delete()
            BaseNotification.objects.filter(id=followed_temp[0].id).delete()
            followed_temp.delete()
            return Response({'status': 'success'})
        return Response({'status': 'you are not followed'}, status=status.HTTP_400_BAD_REQUEST)


class ViewedNotificationAPIView(mixins.UpdateModelMixin, mixins.DestroyModelMixin, GenericAPIView):
    serializer_class = ViewNotificationSerializer

    def patch(self, request, *args, **kwargs):
        try:
            notification = BaseNotification.objects.get(id=self.request.data.get('notification_id'))
            if not notification.is_seen:
                notification.is_seen = True
                notification.save()
                return Response({'status': 'success'})
            else:
                return Response({'status': 'notification is viewed'}, status=status.HTTP_400_BAD_REQUEST)
        except ObjectDoesNotExist:
            return Response({'status': 'error'}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, *args, **kwargs):
        try:
            notification = BaseNotification.objects.get(id=self.request.data.get('notification_id'))
            if notification.is_seen:
                notification.is_seen = False
                notification.save()
                return Response({'status': 'success'})
            else:
                return Response({'status': 'notification is not viewed'}, status=status.HTTP_400_BAD_REQUEST)
        except ObjectDoesNotExist:
            return Response({'status': 'error'}, status=status.HTTP_400_BAD_REQUEST)


class ViewedAllNotificationAPIView(mixins.UpdateModelMixin, mixins.DestroyModelMixin, GenericAPIView):
    serializer_class = ViewNotificationSerializer

    def patch(self, request, *args, **kwargs):
        notifications = BaseNotification.objects.filter(id__in=self.request.data.get('notification_ids'))
        if not notifications.exists():
            return Response({'status': 'nothing to view'})
        for notification in notifications:
            if not notification.is_seen:
                notification.is_seen = True
                notification.save()
        return Response({'status': 'success'})

    def delete(self, request, *args, **kwargs):
        notifications = BaseNotification.objects.filter(id__in=self.request.data.get('notification_ids'))
        if not notifications.exists():
            return Response({'status': 'nothing to unview'})
        for notification in notifications:
            if notification.is_seen:
                notification.is_seen = False
                notification.save()
        return Response({'status': 'success'})
