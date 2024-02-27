from django.contrib.auth.hashers import make_password
from django.utils import timezone
from django.utils.crypto import constant_time_compare, get_random_string
from google.oauth2 import id_token
from google.auth.transport import requests
import jwt

from rest_framework import status
from rest_framework.generics import RetrieveAPIView, ListAPIView, CreateAPIView, DestroyAPIView, \
    ListCreateAPIView, GenericAPIView
from rest_framework.mixins import UpdateModelMixin, DestroyModelMixin
from rest_framework.pagination import LimitOffsetPagination
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken

from apps.events.models import BaseEvent, PermanentEvent
from apps.locations.models import City, Country, Region
from apps.notifications.models import FollowOrg
from apps.profiles.models import User, Organizer, ViewedEvent
from apps.profiles.organizer_filter import OrganizerFilter
from apps.profiles.serializer import ListOrginizerSerializer, UpdateCitySerializer, ProfileSerializer, \
    FollowEventSerializer, LastViewedEventSerializer, MainOrganizerSerializer, OrganizerDetailSerializer, \
    DetailBaseEventSerializer, UserFavouritesSerializer, ChangeUserPictureSerializer, ChangeProfileNamesSerializer, \
    ChangeUserPasswordSerializer, FollowOrganizerSerializer, GoogleOAuthSerializer, \
    AppleOAuthSerializer, DeleteUserSerializer
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.core.exceptions import ObjectDoesNotExist


class ProfileViewSet(RetrieveAPIView):
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = self.request.user.baseprofile.user
        followed_organizers = FollowOrg.objects.filter(user=user).count()
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
            FollowOrg.objects.get(organizer=organizer, user=user)
            return Response({'status': 'already followed'})
        except ObjectDoesNotExist:
            FollowOrg.objects.create(organizer=organizer, user=user)
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
            follow = FollowOrg.objects.get(organizer=organizer, user=user)
            follow.delete()
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
        organizers = Organizer.objects.order_by('-followers').filter(city__city_name=user.city).distinct()[:15]
        followed_organizers = FollowOrg.objects.filter(user=user)
        org_objects_list = [follow.organizer for follow in followed_organizers]
        serialized_data = self.get_serializer(
            organizers,
            many=True,
            context={'request': request, 'followed_organizers': org_objects_list}
        ).data

        return Response(serialized_data)


class DetailOrganizer(RetrieveAPIView):
    serializer_class = OrganizerDetailSerializer
    permission_classes = [IsAuthenticated]
    queryset = Organizer.objects.all()

    def get(self, request, *args, **kwargs):
        organizer = self.get_object()
        followed_organizers = FollowOrg.objects.filter(user=self.request.user.baseprofile.user)
        org_objects_list = [follow.organizer for follow in followed_organizers]
        serialized_data = self.get_serializer(organizer, context={'followed_organizers': org_objects_list,
                                                                  'request': request}).data
        return Response(serialized_data)


class OrganizerEvents(ListAPIView):
    serializer_class = DetailBaseEventSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        event = BaseEvent.objects.get(id=self.kwargs.get('pk'))
        events = BaseEvent.objects.filter(organizer=event.organizer, is_active=True).order_by('-followers')
        return self.paginate_queryset(events)

    def get(self, request, *args, **kwargs):
        serialized_data = self.get_serializer(self.get_queryset(), many=True).data
        return self.get_paginated_response(serialized_data)


class OrganizerEventsDetailOrganizer(ListAPIView):
    serializer_class = DetailBaseEventSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        organizer = Organizer.objects.get(id=self.kwargs.get('pk'))
        events = BaseEvent.objects.filter(organizer=organizer, is_active=True).order_by('-followers')
        return self.paginate_queryset(events)

    def get(self, request, *args, **kwargs):
        serialized_data = self.get_serializer(self.get_queryset(), many=True).data
        return self.get_paginated_response(serialized_data)


class SubscribersUserAPIView(ListAPIView):
    serializer_class = MainOrganizerSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = User.objects.get(id=self.request.user.id)
        subscribers_obj = FollowOrg.objects.filter(user=user)
        org_objects_list = [follow.organizer for follow in subscribers_obj]
        return org_objects_list

    def get(self, request, *args, **kwargs):
        page = self.paginate_queryset(self.get_queryset())
        serializer_data = self.get_serializer(
            page,
            context={'followed_organizers': self.get_queryset(), 'request': request},
            many=True).data
        return self.get_paginated_response(serializer_data)


class FollowEventAPIView(CreateAPIView):
    serializer_class = FollowEventSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        event_id = self.request.data.get('events')
        try:
            event = BaseEvent.objects.get(id=event_id)
        except ObjectDoesNotExist:
            return Response({'status': 'error'}, status=status.HTTP_400_BAD_REQUEST)
        user = self.request.user.baseprofile.user
        if not user.events.filter(id=event.id).exists():
            event.followers += 1
            event.save()
            user.events.add(event)
            user.save()
            return Response({'message': 'Followed to Event', 'is_followed': True})
        return Response({'status': 'Already following this event'}, status=status.HTTP_400_BAD_REQUEST)


class UnFollowEventAPIView(DestroyAPIView):
    serializer_class = FollowEventSerializer
    permission_classes = [IsAuthenticated]

    def delete(self, request, *args, **kwargs):
        user = self.request.user.baseprofile.user
        event_id = self.request.data.get('events')
        try:
            event = BaseEvent.objects.get(id=event_id)
        except ObjectDoesNotExist:
            return Response({'status': 'error'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            user.events.get(id=event.id)
            user.events.remove(event)
            event.followers -= 1
            event.save()
            return Response({'message': 'Unfollowed from Event', 'is_followed': False}, status=status.HTTP_200_OK)
        except ObjectDoesNotExist:
            return Response({'status': 'Not following this event'}, status=status.HTTP_400_BAD_REQUEST)


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
    serializer_class = UpdateCitySerializer

    def patch(self, request, *args, **kwargs):
        user = self.request.user.baseprofile.user
        city_id = self.request.data.get('city')
        try:
            city = City.objects.get(id=city_id)
            user.city = city
            user.save()
            return Response({'status': 'success'})
        except ObjectDoesNotExist:
            return Response({'status': 'error'})


class AllOrganizerListAPIView(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ListOrginizerSerializer
    pagination_class = LimitOffsetPagination

    def get_queryset(self):
        user_city = self.request.user.baseprofile.user.city.city_name
        queryset = Organizer.objects.filter(
            city__city_name=user_city
        )
        return self.paginate_queryset(queryset)

    def get(self, request, *args, **kwargs):
        followed_organizers = FollowOrg.objects.filter(user=self.request.user.baseprofile.user)
        org_objects_list = [follow.organizer for follow in followed_organizers]
        serialized_data = self.get_serializer(
            self.get_queryset(),
            many=True,
            context={'request': request, 'followed_organizers': org_objects_list}
        ).data
        return self.get_paginated_response(serialized_data)


class FilterOrganizerAPIView(ListAPIView):
    serializer_class = MainOrganizerSerializer
    permission_classes = [IsAuthenticated]
    queryset = Organizer.objects.all()
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_class = OrganizerFilter
    search_fields = ['title']

    def get(self, request, *args, **kwargs):
        filtered_queryset = self.filter_queryset(self.get_queryset()).distinct()
        followed_organizers = FollowOrg.objects.filter(user=self.request.user.baseprofile.user)
        org_objects_list = [follow.organizer for follow in followed_organizers]
        serialized_data = self.get_serializer(
            filtered_queryset, many=True,
            context={'followed_organizers': org_objects_list, 'request': request}).data
        return Response(serialized_data)


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


class ChangeUserPasswordAPIView(UpdateModelMixin, GenericAPIView):
    serializer_class = ChangeUserPasswordSerializer
    permission_classes = [IsAuthenticated]

    def patch(self, request, *args, **kwargs):
        user = self.request.user
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
            return Response({
                'access_token': str(access_token),
                'refresh_token': str(refresh_token)
            },
                status=status.HTTP_302_FOUND
            )
        except ObjectDoesNotExist:
            random_password = get_random_string(length=12)
            user = User.objects.create_user(
                email=user_info['email'],
                first_name=user_info['given_name'],
                last_name=user_info['family_name'],
                password=random_password
            )
            user.is_verified = True
            user.save()
            access_token = AccessToken.for_user(user)
            refresh_token = RefreshToken.for_user(user)
            return Response({'access_token': str(access_token), 'refresh_token': str(refresh_token)})


class AppleOAuthAPIView(CreateAPIView):
    serializer_class = AppleOAuthSerializer

    def post(self, request, *args, **kwargs):
        first_name = self.request.data.get('first_name')
        last_name = self.request.data.get('last_name')
        user_apple_token = self.request.data.get('apple_token')
        decoded = jwt.decode(user_apple_token, options={"verify_signature": False})

        try:
            user = User.objects.get(email=decoded['email'])
            access_token = AccessToken.for_user(user)
            refresh_token = RefreshToken.for_user(user)
            return Response({
                'access_token': str(access_token),
                'refresh_token': str(refresh_token)
            },
                status=status.HTTP_302_FOUND
            )
        except ObjectDoesNotExist:
            random_password = get_random_string(length=12)
            user = User.objects.create_user(
                email=decoded['email'],
                first_name=first_name,
                last_name=last_name,
                password=random_password
            )
            user.is_verified = True
            user.save()
            access_token = AccessToken.for_user(user)
            refresh_token = RefreshToken.for_user(user)
            return Response({'access_token': str(access_token), 'refresh_token': str(refresh_token)})


from faker import Faker

fake = Faker()


class AutoParseGeneration(CreateAPIView):
    def post(self, request, *args, **kwargs):
        county_obj = Country.objects.create(country_name='Kyrgyzstan', slug='kyrgyzstan')
        region_obj = Region.objects.create(country=county_obj, region_name='Chui', slug='chui')
        city_obj = City.objects.create(region=region_obj, city_name='Bishkek', slug='bishkek')
        for num in range(1000):
            Organizer.objects.create(
                title=fake.title(),
                back_img='media/media/Screenshot_from_2024-01-09_12-38-58.png',
                description='Долгое время деятельность по организации мероприятий являлась составной частью других отраслей экономики: гостиничного бизнеса, туризма, шоу-бизнеса, часть функций по организации мероприятий была возложена на отделы продаж, профессиональные ассоциации… Это тормозило развитие event management как отдельной формы деятельности.',
                profile_picture='media/media/Screenshot_from_2024-01-09_12-38-58.png',
                city=city_obj,
            )
            PermanentEvent.objects.create(
                title=fake.title(),
                price=fake.number(),
            )


class DeleteUserAPIView(DestroyAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = DeleteUserSerializer

    def delete(self, request, *args, **kwargs):
        try:
            user = self.request.user.baseprofile.user
            user.delete()
            return Response({'status': 'success'})
        except ObjectDoesNotExist:
            return Response({'status': 'user is not found'}, status=status.HTTP_400_BAD_REQUEST)
