from django.urls import path

from .views import EventListAPIView, EventTypeListAPIView, EventDetailAPIView, \
    EventCategoryListAPIView, EventInterestListAPIView, EventTypeFilterAPIView

from .views import EventRetrieveAPIView, EventListAPIView, EventDetailAPIView, \
    EventCategoryListAPIView, EventInterestListAPIView, EventTypeListAPIView


urlpatterns = [
    path("", EventListAPIView.as_view()),
    path("all_id/<int:pk>/", EventRetrieveAPIView.as_view()),
    path("<int:pk>/", EventDetailAPIView.as_view()),
    path("category_list/", EventCategoryListAPIView.as_view()),
    path("interest_list/", EventInterestListAPIView.as_view()),
    path("filter_event_type/", EventTypeFilterAPIView.as_view()),
    path('types/', EventTypeListAPIView.as_view()),
]
