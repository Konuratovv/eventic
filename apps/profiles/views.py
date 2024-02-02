from django.contrib.auth.hashers import make_password
from django.utils import timezone
from django.utils.crypto import constant_time_compare, get_random_string
from google.oauth2 import id_token
from google.auth.transport import requests

from rest_framework import status
from rest_framework.generics import RetrieveAPIView, ListAPIView, CreateAPIView, DestroyAPIView, \
    ListCreateAPIView, GenericAPIView, UpdateAPIView
from rest_framework.mixins import UpdateModelMixin, DestroyModelMixin
from rest_framework.pagination import LimitOffsetPagination
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken

from apps.events.models import BaseEvent
from apps.locations.models import City
from apps.profiles.models import User, Organizer, ViewedEvent
from apps.profiles.organizer_filter import OrganizerFilter
from apps.profiles.serializer import ListOrginizerSerializer, UpdateCitySerializer, ProfileSerializer, \
    FollowEventSerializer, LastViewedEventSerializer, MainOrganizerSerializer, OrganizerDetailSerializer, \
    DetailBaseEventSerializer, UserFavouritesSerializer, ChangeUserPictureSerializer, ChangeProfileNamesSerializer, \
    ChangeUserEmailSerializer, ChangeUserPasswordSerializer, FollowOrganizerSerializer, GoogleOAuthSerializer, \
    AppleOAuthSerializer
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.core.exceptions import ObjectDoesNotExist


class ProfileViewSet(RetrieveAPIView):
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = self.request.user.baseprofile.user
        followed_organizers = user.organizers.count()
        favourites = user.favourites.count()
        serialized_data = self.get_serializer(user).data
        serialized_data['followed_organizers'] = followed_organizers
        serialized_data['favourites'] = favourites
        return Response(serialized_data)


class FollowOrganizerAPIView(CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = FollowOrganizerSerializer

    def post(self, request, *args, **kwargs):
        user = self.request.user.baseprofile.user
        try:
            organizer = Organizer.objects.get(id=self.request.data.get('following'))
        except ObjectDoesNotExist:
            return Response({'status': 'organizer is not found'})

        try:
            user.organizers.get(title=organizer.title)
            return Response({'status': 'already followed'})
        except ObjectDoesNotExist:
            user.organizers.add(organizer)
            organizer.followers += 1
            user.save()
            organizer.save()
            return Response({'status': 'success'})


class UnFollowOrganizerAPIView(DestroyModelMixin, GenericAPIView):
    serializer_class = FollowOrganizerSerializer
    permission_classes = [IsAuthenticated]

    def delete(self, request, *args, **kwargs):
        user = self.request.user.baseprofile.user
        try:
            organizer = Organizer.objects.get(id=self.request.data.get('following'))
        except ObjectDoesNotExist:
            return Response({'status': 'Organizer is not found'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            user.organizers.get(title=organizer.title)
            user.organizers.remove(organizer)
            organizer.followers -= 1
            user.save()
            organizer.save()
            return Response({'status': 'success'})
        except ObjectDoesNotExist:
            return Response({'status': 'user is not followed'})


class OrganizerListAPIView(ListAPIView):
    serializer_class = MainOrganizerSerializer
    permission_classes = [IsAuthenticated]
    queryset = Organizer.objects.all()

    def get(self, request, *args, **kwargs):
        try:
            user = self.request.user.baseprofile.user
        except ObjectDoesNotExist:
            return Response({'status': 'user is not found'})
        organizers = Organizer.objects.order_by('-followers').filter(address__city__city_name=user.city)[:15]
        followed_organizers = user.organizers.all()
        serialized_data = self.get_serializer(
            organizers,
            many=True,
            context={'followed_organizer': followed_organizers, 'request': request}
        ).data

        return Response(serialized_data)


class DetailOrganizer(RetrieveAPIView):
    serializer_class = OrganizerDetailSerializer
    permission_classes = [IsAuthenticated]
    queryset = Organizer.objects.all()

    def get(self, request, *args, **kwargs):
        user = self.request.user.baseprofile.user
        organizer = self.get_object()
        serialized_data = self.get_serializer(organizer, context={'user': user, 'request': request}).data
        return Response(serialized_data)


class OrganizerEvents(ListAPIView):
    serializer_class = DetailBaseEventSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        organizer = Organizer.objects.get(id=self.kwargs.get('pk'))
        events = BaseEvent.objects.filter(organizer=organizer)
        return self.paginate_queryset(events)

    def get(self, request, *args, **kwargs):
        serialized_data = self.get_serializer(self.get_queryset(), many=True).data
        return self.get_paginated_response(serialized_data)


class SubscribersUserAPIView(ListAPIView):
    serializer_class = MainOrganizerSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = User.objects.get(id=self.request.user.id)
        subscribers_obj = user.organizers.all()
        return subscribers_obj

    def get(self, request, *args, **kwargs):
        page = self.paginate_queryset(self.get_queryset())
        serializer_data = self.get_serializer(
            page,
            context={'followed_organizer': self.get_queryset(), 'request': request},
            many=True).data
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


class UserFavouritesAPIView(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserFavouritesSerializer

    def get_queryset(self):
        user = self.request.user.baseprofile.user
        user_favourites = user.favourites.all()
        return self.paginate_queryset(user_favourites)

    def get(self, request, *args, **kwargs):
        serialized_data = self.get_serializer(self.get_queryset(), many=True).data
        return self.get_paginated_response(serialized_data)


class ChangeUserPictureAPIView(UpdateModelMixin, DestroyModelMixin, GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ChangeUserPictureSerializer

    def patch(self, request, *args, **kwargs):
        user = self.request.user.baseprofile.user
        user_photo = self.request.data.get('profile_picture')
        user.profile_picture = user_photo
        user.save()
        return Response({'status': 'success'})


class UpdateCityAPIView(UpdateModelMixin, GenericAPIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, *args, **kwargs):
        user = self.request.user.baseprofile.user
        serializer = UpdateCitySerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({'status': 'success'}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AllOrganizerListAPIView(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ListOrginizerSerializer
    pagination_class = LimitOffsetPagination

    def get_queryset(self):
        user_city = self.request.user.baseprofile.user.city.city_name
        queryset = Organizer.objects.filter(
            address__city__city_name=user_city
        )

        return queryset


class FilterOrganizerAPIView(ListAPIView):
    serializer_class = MainOrganizerSerializer
    permission_classes = [IsAuthenticated]
    queryset = Organizer.objects.all()
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_class = OrganizerFilter
    search_fields = ['title']


class ChangeUserNameAPIView(UpdateModelMixin, GenericAPIView):
    serializer_class = ChangeProfileNamesSerializer
    permission_classes = [IsAuthenticated]

    def patch(self, request, *args, **kwargs):
        user = self.request.user.baseprofile.user
        firstname = self.request.data.get('first_name')
        lastname = self.request.data.get('last_name')
        user.first_name = firstname
        user.last_name = lastname
        user.save()
        return Response({'status': 'success'})


class ChangeUserEmailAPIView(UpdateModelMixin, GenericAPIView):
    serializer_class = ChangeUserEmailSerializer
    permission_classes = [IsAuthenticated]

    def patch(self, request, *args, **kwargs):
        user = self.request.user.baseprofile.user
        email = self.request.data.get('email')
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user.email = email
            user.save()
            return Response({'status': 'success'})
        return Response({'status': 'error'}, status=status.HTTP_400_BAD_REQUEST)


class ChangeUserPasswordAPIView(UpdateModelMixin, GenericAPIView):
    serializer_class = ChangeUserPasswordSerializer
    permission_classes = [IsAuthenticated]

    def patch(self, request, *args, **kwargs):
        user = self.request.user.baseprofile.user
        old_password = self.request.data.get('old_password')
        new_password = self.request.data.get('new_password')
        confirming_new_password = self.request.data.get('confirming_new_password')
        if user.check_password(old_password):
            if constant_time_compare(new_password, confirming_new_password):
                user.password = make_password(confirming_new_password)
                user.save()
                return Response({'status': 'success'})
            return Response({'status': 'error'}, status=status.HTTP_400_BAD_REQUEST)
        return Response({'status': 'error'}, status=status.HTTP_400_BAD_REQUEST)


class GoogleOAuthAPIView(CreateAPIView):
    serializer_class = GoogleOAuthSerializer

    def post(self, request, *args, **kwargs):
        google_token = self.request.data.get('google_token')
        user_info = id_token.verify_oauth2_token(google_token, requests.Request())
        try:
            user = User.objects.get(email=user_info['email'])
            access_token = AccessToken.for_user(user)
            refresh_token = RefreshToken.for_user(user)
            return Response({'access_token': str(access_token), 'refresh_token': str(refresh_token)})
        except ObjectDoesNotExist:
            random_password = get_random_string(length=12)
            user = User.objects.create_user(
                email=user_info['email'],
                first_name=user_info['given_name'],
                last_name=user_info['family_name'],
                password=random_password
            )
            access_token = AccessToken.for_user(user)
            refresh_token = RefreshToken.for_user(user)
            return Response({'access_token': str(access_token), 'refresh_token': str(refresh_token)})


class AppleOAuthAPIView(CreateAPIView):
    serializer_class = AppleOAuthSerializer

    def post(self, request, *args, **kwargs):
        first_name = self.request.data.get('first_name')
        last_name = self.request.data.get('last_name')
        user_apple_email = self.request.data.get('email')

        try:
            user = User.objects.get(email=user_apple_email)
            access_token = AccessToken.for_user(user)
            refresh_token = RefreshToken.for_user(user)
            return Response({'access_token': str(access_token), 'refresh_token': str(refresh_token)})
        except ObjectDoesNotExist:
            random_password = get_random_string(length=12)
            user = User.objects.create_user(
                email=user_apple_email,
                first_name=first_name,
                last_name=last_name,
                password=random_password
            )
            access_token = AccessToken.for_user(user)
            refresh_token = RefreshToken.for_user(user)
            return Response({'access_token': str(access_token), 'refresh_token': str(refresh_token)})
