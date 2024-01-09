from django.urls import path

from .views import EventRetrieveAPIView, EventListAPIView, FreeEventListAPIView, EventTypeListAPIView

urlpatterns = [
    path("", EventListAPIView.as_view()),
    path("<int:pk>/", EventRetrieveAPIView.as_view()),
    path('types/', EventTypeListAPIView.as_view()),
    path("free_events/", FreeEventListAPIView.as_view()),
]
