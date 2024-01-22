from django.urls import path

from .views import EventListAPIView, EventDetailAPIView, \
    EventCategoryListAPIView, EventInterestListAPIView, EventTypeListAPIView, \
    EventTypeFilterAPIView, FreeEventListAPIView, AllEventsListAPIView, AllFreeEventsListAPIView, AllPaidEventsListAPIView, AllPermEventsListAPIView, AllTempEventsListAPIView

urlpatterns = [
    path("", EventListAPIView.as_view()),
    path("<int:pk>/", EventDetailAPIView.as_view()),
    path("category_list/", EventCategoryListAPIView.as_view()),
    path("interest_list/", EventInterestListAPIView.as_view()),
    path("free_events_list/", FreeEventListAPIView.as_view()),
    path("filter_event_type/", EventTypeFilterAPIView.as_view()),
    path('types/', EventTypeListAPIView.as_view()),
    path('types/all-events/', AllEventsListAPIView.as_view()),
    path('types/free-events/', AllFreeEventsListAPIView.as_view()),
    path('types/paid-events/', AllPaidEventsListAPIView.as_view()),
    path('types/temporary-events/', AllTempEventsListAPIView.as_view()),
    path('types/permanent-events/', AllPermEventsListAPIView.as_view()),
]
