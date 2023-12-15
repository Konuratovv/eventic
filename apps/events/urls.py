from django.urls import path

from .views import EventRetrieveAPIView, EventListAPIView

urlpatterns = [
    path("", EventListAPIView.as_view()),
    path("<int:pk>/", EventRetrieveAPIView.as_view()),
]
