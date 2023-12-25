from django.contrib.auth.hashers import make_password
from rest_framework import status
from rest_framework.generics import RetrieveAPIView, ListAPIView, CreateAPIView, DestroyAPIView, UpdateAPIView

from apps.events.models import BaseEvent
from apps.events.serializers import EventSerializer
from apps.profiles.models import User, Organizer, FollowOrganizer
from apps.profiles.serializer import ProfileSerializer, OrganizerSerializer, FollowOrganizerSerializer, \
    FollowEventSerializer, ChangePasswordSerializer, SubscribersUserSerializer
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.core.exceptions import ObjectDoesNotExist
from django.utils.crypto import constant_time_compare

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
                FollowOrganizer.objects.get(follower=user, following=organizer)
                return Response({'error': 'Already following this organizer'}, status=status.HTTP_400_BAD_REQUEST)
            except ObjectDoesNotExist:
                follow = FollowOrganizer.objects.create(follower=user, following=organizer)
                follow.is_followed = True
                follow.save()
                return Response({'message': 'Followed', 'status': f'{follow.is_followed}'})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UnFollowOrganizerAPIView(DestroyAPIView):
    serializer_class = FollowOrganizerSerializer
    permission_classes = [IsAuthenticated]

    def delete(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        user = User.objects.get(id=self.request.user.id)

        try:
            organizer = Organizer.objects.get(id=self.request.data.get('following'))
        except ObjectDoesNotExist:
            return Response({'error': 'Organizer not found'}, status=status.HTTP_404_NOT_FOUND)

        if serializer.is_valid():
            try:
                existing_follow = FollowOrganizer.objects.get(follower=user, following=organizer)
            except ObjectDoesNotExist:
                return Response({'status': "follow is not exist"})
            existing_follow.is_followed = False
            existing_follow.save()
            return Response({'message': 'Unfollowed', 'status': False}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class FollowersOrganizerAPIView(ListAPIView):
    serializer_class = OrganizerSerializer
    queryset = Organizer.objects.all()
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        organizers = self.get_queryset()
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


class FollowersEventAPIView(ListAPIView):
    queryset = BaseEvent.objects.all()
    serializer_class = EventSerializer
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        events = self.get_queryset()
        data = []
        for event in events:
            followers = event.users.count()
            serializer = self.get_serializer(event)
            data.append({'event_data': serializer.data, 'followers_count': followers})

        sorted_data = sorted(data, key=lambda x: x['followers_count'], reverse=True)

        return Response(sorted_data)


class FollowEventAPIView(CreateAPIView):
    serializer_class = FollowEventSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        user = User.objects.get(id=self.request.user.id)
        return user

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        event_id = self.request.data.get('events')
        if serializer.is_valid():
            user = self.get_object()
            event = BaseEvent.objects.get(id=event_id)
            if user.events.get(id=event.id):
                return Response({'status': 'Already following this event'}, status=status.HTTP_400_BAD_REQUEST)
            user.events.add(event)
            user.save()
            return Response({'status': 'Followed to Event'}, status=status.HTTP_200_OK)
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
                return Response({'status': 'Unfollowed from Event'}, status=status.HTTP_200_OK)
            except ObjectDoesNotExist:
                return Response({'status': 'Not following this event'}, status=status.HTTP_400_BAD_REQUEST)
        return Response({'status': 'event is not found'}, status=status.HTTP_400_BAD_REQUEST)


class SendResetAPiView(UpdateAPIView):
    serializer_class = SendResetCodeSerializer

    def get_object(self):
        user = CustomUser.objects.get(email=self.request.data.get('email'))
        return user

    def patch(self, request, *args, **kwargs):
        email = self.get_object().email
        send_verification_mail(email)
        return Response({'message': 'Reset code have sent successfully'})


class CheckResetCodeAPIView(UpdateAPIView):
    serializer_class = CodeSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        user = User.objects.get(id=self.request.user.id)
        return user

    def patch(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = self.get_object()
            code = self.request.data.get('code')
            if user.code == code:
                user.code = None
                user.save()
                return Response({'status': 'success'}, status=status.HTTP_200_OK)
            else:
                return Response({'status': 'invalid code'}, status=status.HTTP_400_BAD_REQUEST)
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
