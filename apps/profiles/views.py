from datetime import timedelta

from django.conf import settings
from django.db.models import BooleanField, Case, When, Value
from django.utils import timezone

from django.contrib.auth.hashers import make_password
from rest_framework import status
from rest_framework.generics import RetrieveAPIView, ListAPIView, CreateAPIView, DestroyAPIView, UpdateAPIView, \
    ListCreateAPIView
from rest_framework.pagination import PageNumberPagination

from apps.events.models import BaseEvent
from apps.profiles.models import User, Organizer, FollowOrganizer, ViewedEvent
from apps.profiles.serializer import ProfileSerializer, OrganizerSerializer, FollowOrganizerSerializer, \
    FollowEventSerializer, ChangePasswordSerializer, LastViewedEventSerializer, LastViewedEventReadSerializer
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.core.exceptions import ObjectDoesNotExist
from django.utils.crypto import constant_time_compare
from rest_framework_simplejwt.tokens import AccessToken

from apps.users.serializer import CodeSerializer
from apps.users.utils import send_verification_mail

from apps.users.models import CustomUser
from apps.profiles.serializer import SendResetCodeSerializer


class ProfileViewSet(RetrieveAPIView):
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]

    def retrieve(self, request, *args, **kwargs):
        user = User.objects.get(id=self.request.user.id)
        serializer = self.get_serializer(user)
        return Response(serializer.data)


class FollowOrganizerAPIView(CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = FollowOrganizerSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        user = User.objects.get(id=self.request.user.id)
        try:
            organizer = Organizer.objects.get(id=self.request.data.get('following'))
        except ObjectDoesNotExist:
            return Response({'error': 'Organizer not found'}, status=status.HTTP_404_NOT_FOUND)

        if serializer.is_valid():
            follow = FollowOrganizer.objects.filter(follower=user, following=organizer, is_followed=True)
            if follow:
                return Response({'status': 'you are already exists'})
            try:
                follow = FollowOrganizer.objects.get(follower=user, following=organizer, is_followed=False)
                follow.is_followed = True
                follow.save()
                return Response({'message': 'followed', 'status': f'{follow.is_followed}'}, status=status.HTTP_200_OK)
            except ObjectDoesNotExist:
                follow = FollowOrganizer.objects.create(follower=user, following=organizer)
                follow.is_followed = True
                follow.save()
                return Response({'message': 'Followed', 'status': f'{follow.is_followed}'})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UnFollowOrganizerAPIView(UpdateAPIView):
    serializer_class = FollowOrganizerSerializer
    permission_classes = [IsAuthenticated]

    def patch(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        user = User.objects.get(id=self.request.user.id)

        try:
            organizer = Organizer.objects.get(id=self.request.data.get('following'))
        except ObjectDoesNotExist:
            return Response({'error': 'Organizer not found'}, status=status.HTTP_404_NOT_FOUND)

        if serializer.is_valid():
            try:
                existing_follow = FollowOrganizer.objects.get(follower=user, following=organizer, is_followed=True)
            except ObjectDoesNotExist:
                return Response({'status': "follow is not exist"})
            existing_follow.is_followed = False
            existing_follow.save()
            return Response({'message': 'Unfollowed', 'status': False}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class OrganizerListAPIView(ListAPIView):
    serializer_class = OrganizerSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        try:
            user = User.objects.get(id=self.request.user.id)
        except ObjectDoesNotExist:
            return Response({'status': 'user is not found'})

        is_follow_sub = FollowOrganizer.objects.filter(follower=user, is_followed=True).values('following__pk')

        organizers = Organizer.objects.annotate(
            is_follow=Case(
                When(id__in=is_follow_sub, then=Value(True)),
                default=Value(False),
                output_field=BooleanField()
            )
        )

        data = []
        for organizer in organizers:
            followers = organizer.followers.count()
            serializer_data = self.get_serializer(organizer).data

            data.append({"organizer_data": serializer_data, 'followers_count': followers})

        sorted_data = sorted(data, key=lambda x: x['followers_count'], reverse=True)
        return Response(sorted_data)


class DetailOrganizer(RetrieveAPIView):
    serializer_class = OrganizerSerializer
    queryset = Organizer.objects.all()

    def get(self, request, *args, **kwargs):
        organizer = self.get_object()
        serializer = self.get_serializer(organizer)
        return Response(serializer.data)


class SubscribersUserAPIView(ListAPIView):
    serializer_class = OrganizerSerializer
    queryset = FollowOrganizer.objects.all()
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = User.objects.get(id=self.request.user.id)
        subscribers_obj = user.following.filter(is_followed=True)
        organizers = [subscriber.following for subscriber in subscribers_obj]
        serializer = self.get_serializer(organizers, many=True)
        return Response(serializer.data)


class FollowEventAPIView(CreateAPIView):
    serializer_class = FollowEventSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        event_id = self.request.data.get('events')
        if serializer.is_valid():
            user = User.objects.get(id=self.request.user.id)
            event = BaseEvent.objects.get(id=event_id)
            if not user.events.filter(id=event.id).exists():
                user.add(event)
                user.save()
                return Response({'message': 'Followed to Event', 'is_followed': True}, status=status.HTTP_200_OK)
            return Response({'status': 'Already following this event'}, status=status.HTTP_400_BAD_REQUEST)
        return Response({'status': 'Event not found'}, status=status.HTTP_404_NOT_FOUND)


class UnFollowEventAPIView(DestroyAPIView):
    serializer_class = FollowEventSerializer
    permission_classes = [IsAuthenticated]

    def delete(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        user = User.objects.get(id=self.request.user.id)
        event_id = self.request.data.get('events')
        if serializer.is_valid():
            event = BaseEvent.objects.get(id=event_id)
            try:
                user.events.get(id=event.id)
                user.events.remove(event)
                return Response({'message': 'Unfollowed from Event', 'is_followed': False}, status=status.HTTP_200_OK)
            except ObjectDoesNotExist:
                return Response({'status': 'Not following this event'}, status=status.HTTP_400_BAD_REQUEST)
        return Response({'status': 'event is not found'}, status=status.HTTP_400_BAD_REQUEST)


class SendResetAPiView(UpdateAPIView):
    serializer_class = SendResetCodeSerializer

    def get_object(self):
        user = CustomUser.objects.get(email=self.request.data.get('email'))
        return user

    def patch(self, request, *args, **kwargs):
        try:
            email = self.get_object().email
        except ObjectDoesNotExist:
            return Response({'status': 'error'}, status=status.HTTP_400_BAD_REQUEST)
        send_verification_mail(email)
        return Response({'status': 'success'}, status=status.HTTP_200_OK)


class CheckResetCodeAPIView(UpdateAPIView):
    serializer_class = CodeSerializer

    def patch(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            code = self.request.data.get('code')
            try:
                user = CustomUser.objects.get(code=code)
                user.code = None
                user.save()
            except ObjectDoesNotExist:
                return Response({'status': 'error'}, status=status.HTTP_400_BAD_REQUEST)
            else:
                access_token = AccessToken.for_user(user)
                access_token.set_exp(lifetime=timedelta(minutes=15))
                return Response({'status': 'success', 'access_token': str(access_token)}, status=status.HTTP_200_OK)
        return Response({'status': 'error'}, status=status.HTTP_400_BAD_REQUEST)


class ChangePasswordAPIVIew(UpdateAPIView):
    serializer_class = ChangePasswordSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        user = User.objects.get(id=self.request.user.id)
        return user

    def patch(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=self.request.data)
        if serializer.is_valid():
            new_password = self.request.data.get('new_password')
            confirming_new_password = self.request.data.get('confirming_new_password')
            if constant_time_compare(new_password, confirming_new_password):
                user = self.get_object()
                user.password = make_password(confirming_new_password)
                user.save()
                return Response({'status': 'success'}, status=status.HTTP_200_OK)
            else:
                return Response({'status': 'error'}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors)


class LastViewedEvents(ListCreateAPIView):
    serializer_class = LastViewedEventSerializer
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return LastViewedEventSerializer
        else:
            return LastViewedEventReadSerializer

    def get_queryset(self):
        user = User.objects.get(id=self.request.user.id)
        return user.last_viewed_events.order_by('-timestamp')

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=self.request.data)
        try:
            if serializer.is_valid():
                user = User.objects.get(id=self.request.user.id)
                event = BaseEvent.objects.get(id=self.request.data.get('event'))
                viewed_event = ViewedEvent.objects.filter(user=user, event=event)
                if not viewed_event:
                    viewed_event = ViewedEvent.objects.create(user=user, event=event)
                    viewed_event.save()
                    user.last_viewed_events.add(viewed_event)
                    user.save()
                    return Response({'status': 'success'}, status=status.HTTP_200_OK)
                else:
                    viewed_event = viewed_event[0]
                    viewed_event.timestamp = timezone.now()
                    viewed_event.save()
                    user.last_viewed_events.add(viewed_event)
                    user.save()
                    return Response({'status': 'success'}, status=status.HTTP_200_OK)
            return Response({'status': 'error'}, status=status.HTTP_400_BAD_REQUEST)
        except ObjectDoesNotExist:
            return Response({'status': 'error'}, status=status.HTTP_400_BAD_REQUEST)
