from django.urls import path

from apps.profiles.views import ProfileViewSet, FollowOrganizerAPIView, FollowersOrganizerAPIView, FollowEventAPIView, \
    FollowersEventAPIView, UnFollowOrganizerAPIView, UnFollowEventAPIView, SendResetAPiView, CheckResetCodeAPIView, \
    ChangePasswordAPIVIew, SubscribersUserAPIView
from apps.users.views import SendCodeAPIView, VerifyAPIView

urlpatterns = [
    path('profile/', ProfileViewSet.as_view()),
    path('follow/organizer/', FollowOrganizerAPIView.as_view()),
    path('unfollow/organizer/', UnFollowOrganizerAPIView.as_view()),
    path('followers/organizer/', FollowersOrganizerAPIView.as_view()),
    path('subscribers/user/', SubscribersUserAPIView.as_view()),
    path('send_verify_code/', SendCodeAPIView.as_view()),
    path('verify/email/', VerifyAPIView.as_view()),
    path('follow/event/', FollowEventAPIView.as_view()),
    path('followers/event/', FollowersEventAPIView.as_view()),
    path('unfollow/event/', UnFollowEventAPIView.as_view()),
    path('send_reset_code/', SendResetAPiView.as_view()),
    path('check_reset_code/', CheckResetCodeAPIView.as_view()),
    path('change_password/', ChangePasswordAPIVIew.as_view())
]
