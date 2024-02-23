from django.urls import path
from .views import AllPopularEventsListAPIView, EventListAPIView, EventDetailAPIView, \
    EventCategoryListAPIView, EventInterestListAPIView, EventTypeListAPIView, EventTypeFilterAPIView, \
    AllEventsListAPIView, AllFreeEventsListAPIView, AllPermEventsListAPIView, \
    OrganizerEventsAPIView, EventsByInterestsAPIView, NextEventsOrgAPIView, \
    RelatedEventsByInterestAPIView

urlpatterns = [
    path("", EventListAPIView.as_view()),
    path("<int:pk>/", EventDetailAPIView.as_view()),
    path('<int:pk>/next_events_org/', NextEventsOrgAPIView.as_view()),
    path('<int:pk>/related_events_by_interest/', RelatedEventsByInterestAPIView.as_view()),
    path("category_list/", EventCategoryListAPIView.as_view()),
    path("interest_list/", EventInterestListAPIView.as_view()),
    path("filter_event_type/", EventTypeFilterAPIView.as_view()),
    path('types/', EventTypeListAPIView.as_view()),
    path('types/all-events/', AllEventsListAPIView.as_view()),
    path('types/all-free-events/', AllFreeEventsListAPIView.as_view()),
    path('types/all-permanent-events/', AllPermEventsListAPIView.as_view()),
    path('types/all-popular-events/', AllPopularEventsListAPIView.as_view()),
    path('all-organizer-events/<int:pk>/', OrganizerEventsAPIView.as_view()),
    path('all-interests-events/<int:pk>/', EventsByInterestsAPIView.as_view()),
]
