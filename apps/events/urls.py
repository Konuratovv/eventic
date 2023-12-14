from django.urls import path

from .views import EventRetrieveAPIView, EventListApiView

urlpatterns = [
    path("", EventListApiView.as_view()),
    path("event/<int:pk>/", EventRetrieveAPIView.as_view()),
]
