from django.urls import path

from apps.profiles.views import ProfileViewSet, FollowOrganizerAPIView, OrganizerListAPIView, FollowEventAPIView, \
    UnFollowOrganizerAPIView, UnFollowEventAPIView, SubscribersUserAPIView, LastViewedEvents, \
    DetailOrganizer, OrganizerEvents, UserFavourites

urlpatterns = [
    path('profile/', ProfileViewSet.as_view()),
    path('follow/organizer/', FollowOrganizerAPIView.as_view()),
    path('unfollow/organizer/', UnFollowOrganizerAPIView.as_view()),
    path('organizers/', OrganizerListAPIView.as_view()),
    path('organizer/<int:pk>/', DetailOrganizer.as_view()),
    path('subscribers/user/', SubscribersUserAPIView.as_view()),
    path('follow/event/', FollowEventAPIView.as_view()),
    path('unfollow/event/', UnFollowEventAPIView.as_view()),
    path('last_viewed_events/', LastViewedEvents.as_view()),
    path('events/organizer/<int:pk>/', OrganizerEvents.as_view()),
    path('user_favourites/', UserFavourites.as_view()),
]
