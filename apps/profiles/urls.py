from django.urls import path

from apps.profiles.views import ProfileViewSet, FollowOrganizerAPIView, OrganizerListAPIView, FollowEventAPIView, \
    UnFollowOrganizerAPIView, UnFollowEventAPIView, SubscribersUserAPIView, LastViewedEvents, \
    DetailOrganizer, OrganizerEvents, UpdateCityAPIView, UserFavourites, ChangeUserPictureAPIView, AllOrganizerListAPIView, FilterOrganizerAPIView

urlpatterns = [
    path('profile/', ProfileViewSet.as_view()),
    path('follow/organizer/', FollowOrganizerAPIView.as_view()),
    path('unfollow/organizer/', UnFollowOrganizerAPIView.as_view()),
    path('organizers/', OrganizerListAPIView.as_view()),
    path('organizer-search/', FilterOrganizerAPIView.as_view()),
    path('organizer/<int:pk>/', DetailOrganizer.as_view()),
    path('subscribers/user/', SubscribersUserAPIView.as_view()),
    path('follow/event/', FollowEventAPIView.as_view()),
    path('unfollow/event/', UnFollowEventAPIView.as_view()),
    path('last_viewed_events/', LastViewedEvents.as_view()),
    path('events/organizer/<int:pk>/', OrganizerEvents.as_view()),
    path('user_favourites/', UserFavourites.as_view()),
    path('change_profile_picture/', ChangeUserPictureAPIView.as_view()),
    path('update-city/', UpdateCityAPIView.as_view()),
    path('all-organizers/', AllOrganizerListAPIView.as_view())
]
