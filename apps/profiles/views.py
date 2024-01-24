from django.db.models import BooleanField, Case, When, Value
from django.utils import timezone

from rest_framework import status
from rest_framework.generics import RetrieveAPIView, ListAPIView, CreateAPIView, DestroyAPIView, \
    ListCreateAPIView, GenericAPIView
from rest_framework.mixins import UpdateModelMixin

from apps.events.models import BaseEvent
from apps.profiles.models import User, Organizer, FollowOrganizer, ViewedEvent
from apps.profiles.serializer import ProfileSerializer, FollowOrganizerSerializer, \
    FollowEventSerializer, LastViewedEventSerializer, MainOrganizerSerializer, OrganizerDetailSerializer, \
    DetailBaseEventSerializer, UserFavouritesSerializer, ChangeUserPictureSerializer
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.core.exceptions import ObjectDoesNotExist


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


class UnFollowOrganizerAPIView(UpdateModelMixin, GenericAPIView):
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
    serializer_class = MainOrganizerSerializer
    permission_classes = [IsAuthenticated]
    queryset = Organizer.objects.all()

    def get(self, request, *args, **kwargs):
        try:
            user = User.objects.get(id=self.request.user.id)
        except ObjectDoesNotExist:
            return Response({'status': 'user is not found'})

        is_follow_sub = FollowOrganizer.objects.filter(follower=user, is_followed=True).values('following__pk')

        organizers = self.queryset.annotate(
            is_followed=Case(
                When(id__in=is_follow_sub, then=Value(True)),
                default=Value(False),
                output_field=BooleanField()
            )
        )

        page = self.paginate_queryset(organizers)

        data = []
        if page is not None:
            for organizer in page:
                followers = organizer.followers.filter(is_followed=True).count()
                serializer_data = self.get_serializer(organizer).data

                data.append({"organizer_data": serializer_data, 'followers_count': followers})

            sorted_data = sorted(data, key=lambda x: x['followers_count'], reverse=True)
            result_data = [organizer['organizer_data'] for organizer in sorted_data]
            return self.get_paginated_response(result_data)


class DetailOrganizer(RetrieveAPIView):
    serializer_class = OrganizerDetailSerializer
    permission_classes = [IsAuthenticated]
    queryset = Organizer.objects.all()

    def get(self, request, *args, **kwargs):
        user = User.objects.get(id=self.request.user.id)
        organizer = self.get_object()
        followed_id = FollowOrganizer.objects.filter(follower=user, is_followed=True).values('following__pk')
        organizer.is_followed = any(event_id['following__pk'] == organizer.pk for event_id in followed_id)
        serialized_data = self.get_serializer(organizer).data
        return Response(serialized_data)


class OrganizerEvents(ListAPIView):
    serializer_class = DetailBaseEventSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # user = User.objects.get(id=self.request.user.id)
        organizer = Organizer.objects.get(id=self.kwargs.get('pk'))
        events = BaseEvent.objects.filter(organizer=organizer)
        return self.paginate_queryset(events)

    def get(self, request, *args, **kwargs):
        serialized_data = self.get_serializer(self.get_queryset(), many=True).data
        return self.get_paginated_response(serialized_data)


class SubscribersUserAPIView(ListAPIView):
    serializer_class = MainOrganizerSerializer
    queryset = FollowOrganizer.objects.all()
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = User.objects.get(id=self.request.user.id)
        followed_id = FollowOrganizer.objects.filter(follower=user, is_followed=True).values('following__pk')
        subscribers_obj = user.following.filter(is_followed=True)

        organizers = [subscriber.following for subscriber in subscribers_obj]

        page = self.paginate_queryset(organizers)

        for organizer in page:
            organizer.is_followed = any(event_id['following__pk'] == organizer.pk for event_id in followed_id)
        serializer_data = self.get_serializer(page, many=True).data
        return self.get_paginated_response(serializer_data)


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
                event.followers += 1
                event.save()
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
                event.followers -= 1
                event.save()
                return Response({'message': 'Unfollowed from Event', 'is_followed': False}, status=status.HTTP_200_OK)
            except ObjectDoesNotExist:
                return Response({'status': 'Not following this event'}, status=status.HTTP_400_BAD_REQUEST)
        return Response({'status': 'event is not found'}, status=status.HTTP_400_BAD_REQUEST)


class LastViewedEvents(ListCreateAPIView):
    serializer_class = LastViewedEventSerializer
    permission_classes = [IsAuthenticated]

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


class UserFavourites(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserFavouritesSerializer

    def get_queryset(self):
        user = self.request.user.baseprofile.user
        user_favourites = user.favourites.all()
        return user_favourites

    def get(self, request, *args, **kwargs):
        serialized_data = self.get_serializer(self.get_queryset(), many=True).data
        return Response(serialized_data)


class ChangeUserPictureAPIView(UpdateModelMixin, GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ChangeUserPictureSerializer

    def patch(self, request, *args, **kwargs):
        user = self.request.user.baseprofile.user
        user_photo = self.request.data.get('profile_picture')
        user.profile_picture = user_photo
        user.save()
        return Response({'status': 'success'})
