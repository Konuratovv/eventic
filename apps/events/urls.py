from django.urls import path
from .views import EventListAPIView, EventDetailAPIView, \
    EventCategoryListAPIView, EventInterestListAPIView, EventTypeListAPIView, EventTypeFilterAPIView, \
    NextEventsOrgAPIView, RelatedEventsByInterestAPIView

urlpatterns = [
    path("", EventListAPIView.as_view()),
    path("<int:pk>/", EventDetailAPIView.as_view()),
    path('<int:pk>/next_events_org/', NextEventsOrgAPIView.as_view()),
    path('<int:pk>/related_events_by_interest/', RelatedEventsByInterestAPIView.as_view()),
    path("category_list/", EventCategoryListAPIView.as_view()),
    path("interest_list/", EventInterestListAPIView.as_view()),
    path("filter_event_type/", EventTypeFilterAPIView.as_view()),
    path('types/', EventTypeListAPIView.as_view()),

]
