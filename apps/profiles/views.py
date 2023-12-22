from rest_framework import status
from rest_framework.generics import RetrieveAPIView, UpdateAPIView, ListAPIView, CreateAPIView, DestroyAPIView

from apps.events.models import Event
from apps.events.serializers import EventSerializer
from apps.profiles.models import User, Organizer, FollowOrganizer
from apps.profiles.serializer import ProfileSerializer, OrganizerSerializer, FollowOrganizerSerializer, \
    FollowEventSerializer
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.core.exceptions import ObjectDoesNotExist


class ProfileViewSet(RetrieveAPIView):
    serializer_class = ProfileSerializer

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
                existing_follow = FollowOrganizer.objects.get(follower=user, following=organizer)
                return Response({'error': 'Already following this organizer'}, status=status.HTTP_400_BAD_REQUEST)
            except ObjectDoesNotExist:
                follow = FollowOrganizer.objects.create(follower=user, following=organizer)
                follow.save()
                return Response({'message': 'Followed'})
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
            existing_follow.delete()
            return Response({'status': 'Unfollowed'}, status=status.HTTP_200_OK)
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


class FollowersEventAPIView(ListAPIView):
    queryset = Event.objects.all()
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
            event = Event.objects.get(id=event_id)
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
            event = Event.objects.get(id=event_id)
            try:
                user.events.get(id=event.id)
                user.events.remove(event)
                return Response({'status': 'Unfollowed from Event'}, status=status.HTTP_200_OK)
            except ObjectDoesNotExist:
                return Response({'status': 'Not following this event'}, status=status.HTTP_400_BAD_REQUEST)
        return Response({'status': 'event is not found'}, status=status.HTTP_400_BAD_REQUEST)
