from django.urls import path

from .views import EventRetrieveAPIView, EventListAPIView, EventTypeListAPIView, EventDetailAPIView, \
    EventCategoryListAPIView, EventInterestListAPIView, FollowOrganizerView

urlpatterns = [
    path("", EventListAPIView.as_view()),
    path("all_id/<int:pk>/", EventRetrieveAPIView.as_view()),
    path("<int:pk>/", EventDetailAPIView.as_view()),
    path("category_list/", EventCategoryListAPIView.as_view()),
    path("interest_list/", EventInterestListAPIView.as_view()),
    path('types/', EventTypeListAPIView.as_view()),

    # Подписка и отписка от организатора в детейле
    path('organizer/<int:organizer_id>/follow/', FollowOrganizerView.as_view(), name='follow-organizer'),
    path('organizer/<int:organizer_id>/unfollow/', FollowOrganizerView.as_view(), name='unfollow-organizer'),
]
