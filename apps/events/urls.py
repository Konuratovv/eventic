from django.urls import path
from .views import EventListAPIView, EventDetailAPIView, \
    EventCategoryListAPIView, EventInterestListAPIView, EventTypeListAPIView, EventTypeFilterAPIView, \
    FreeEventListAPIView, AllEventsListAPIView, AllFreeEventsListAPIView, AllPaidEventsListAPIView, AllPermEventsListAPIView, AllTempEventsListAPIView, OrganizerEventsAPIView, EventsByInterestsAPIView
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
    path('types/all-events/', AllEventsListAPIView.as_view()),
    path('types/all-free-events/', AllFreeEventsListAPIView.as_view()),
    path('types/all-paid-events/', AllPaidEventsListAPIView.as_view()),
    path('types/all-permanent-events/', AllPermEventsListAPIView.as_view()),
    path('types/all-temporary-events/', AllTempEventsListAPIView.as_view()),
    path('all-organizer-events/', OrganizerEventsAPIView.as_view()),
    path('all-interests-events/', EventsByInterestsAPIView.as_view()),
]
