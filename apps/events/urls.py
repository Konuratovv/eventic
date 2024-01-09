from django.urls import path

from .views import EventRetrieveAPIView, EventListAPIView, EventTypeListAPIView, EventDetailAPIView

urlpatterns = [
    path("", EventListAPIView.as_view()),
    path("all_id/<int:pk>/", EventRetrieveAPIView.as_view()),
    path("<int:pk>/", EventDetailAPIView.as_view()),
    path('types/', EventTypeListAPIView.as_view()),
]
