from django.urls import path

from apps.profiles.views import ProfileViewSet, FollowOrganizerAPIView, OrganizerListAPIView, FollowEventAPIView, \
    EventTypeListAPIView, UnFollowOrganizerAPIView, UnFollowEventAPIView, SubscribersUserAPIView, LastViewedEvents, \
    DetailOrganizer

urlpatterns = [
    path('profile/', ProfileViewSet.as_view()),
    path('follow/organizer/', FollowOrganizerAPIView.as_view()),
    path('unfollow/organizer/', UnFollowOrganizerAPIView.as_view()),
    path('organizers/', OrganizerListAPIView.as_view()),
    path('organizer/<int:pk>/', DetailOrganizer.as_view()),
    path('subscribers/user/', SubscribersUserAPIView.as_view()),
    path('follow/event/', FollowEventAPIView.as_view()),
    path('events_types/', EventTypeListAPIView.as_view()),
    path('unfollow/event/', UnFollowEventAPIView.as_view()),
    path('last_viewed_events/', LastViewedEvents.as_view()),
]
