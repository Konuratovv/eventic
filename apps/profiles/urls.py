from django.urls import path

from apps.profiles.views import ProfileViewSet, FollowOrganizerAPIView, FollowersOrganizerAPIView, FollowEventAPIView, \
    FollowersEventAPIView, UnFollowOrganizerAPIView, UnFollowEventAPIView
from apps.users.views import SendCodeAPIView, VerifyAPIView

urlpatterns = [
    path('profile/', ProfileViewSet.as_view()),
    path('follow/organizer/', FollowOrganizerAPIView.as_view()),
    path('unfollow/organizer/', UnFollowOrganizerAPIView.as_view()),
    path('followers/organizer/', FollowersOrganizerAPIView.as_view()),
    path('send_code/', SendCodeAPIView.as_view()),
    path('verify/email/', VerifyAPIView.as_view()),
    path('follow/event/', FollowEventAPIView.as_view()),
    path('followers/event/', FollowersEventAPIView.as_view()),
    path('unfollow/event/', UnFollowEventAPIView.as_view())
]
