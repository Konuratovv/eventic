from datetime import timedelta

from django.contrib.auth.hashers import make_password
from rest_framework import status
from rest_framework.generics import RetrieveAPIView, ListAPIView, CreateAPIView, DestroyAPIView, UpdateAPIView

from apps.events.models import BaseEvent, TemporaryEvent, PermanentEvent
from apps.events.serializers import EventSerializer
from apps.profiles.models import User, Organizer, FollowOrganizer
from apps.profiles.serializer import ProfileSerializer, OrganizerSerializer, FollowOrganizerSerializer, \
    FollowEventSerializer, ChangePasswordSerializer, PermanentEventSerializer, TemporaryEventSerializer
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.core.exceptions import ObjectDoesNotExist
from django.utils.crypto import constant_time_compare
from rest_framework_simplejwt.tokens import AccessToken
from operator import itemgetter

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
        user = User.objects.get(id=self.request.user.id)
        user_organizers = FollowOrganizer.objects.filter(follower=user, is_followed=True).values_list('following',
                                                                                                      flat=True)
        organizers = Organizer.objects.exclude(id__in=user_organizers)
        print(organizers)

        data = []
        for organizer in organizers:
            followers = organizer.followers.count()
            serializer = self.get_serializer(organizer)
            data.append({"organizer_data": serializer.data, 'followers_count': followers})

        sorted_data = sorted(data, key=lambda x: x['followers_count'], reverse=True)
        return Response(sorted_data)


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


class EventListAPIView(ListAPIView):
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        data = {}
        for event in BaseEvent.objects.all():
            serializer_data = EventSerializer(event).data
            serializer_data['followers'] = event.users.count()
            data.setdefault('events', []).append(serializer_data)
        for perEvent in PermanentEvent.objects.all():
            serializer_data = PermanentEventSerializer(perEvent).data
            serializer_data['followers'] = perEvent.users.count()
            data.setdefault('perEvents', []).append(serializer_data)
        for temEvent in TemporaryEvent.objects.all():
            serializer_data = TemporaryEventSerializer(temEvent).data
            serializer_data['followers'] = temEvent.users.count()
            data.setdefault('temEvents', []).append(serializer_data)

        sorted_data = {
            'events': sorted(data['events'], key=itemgetter('followers'), reverse=True),
            'perEvents': sorted(data['perEvents'], key=itemgetter('followers'), reverse=True),
            'temEvents': sorted(data['temEvents'], key=itemgetter('followers'), reverse=True),
        }
        return Response(sorted_data)


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
                user.events.add(event)
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
            return Response({'status': 'Invalid email'})
        send_verification_mail(email)
        return Response({'message': 'Reset code have sent successfully'})


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
                return Response({'status': 'Invalid code'})
            else:
                access_token = AccessToken.for_user(user)
                access_token.set_exp(lifetime=timedelta(minutes=15))
                return Response({'status': 'success', 'access_token': str(access_token)}, status=status.HTTP_200_OK)
        return Response({'error': 'invalid serializer'})


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
                return Response({'status': 'password changed successfully'}, status=status.HTTP_200_OK)
            else:
                return Response({'status': 'password is not match'}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors)
