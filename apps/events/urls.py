from django.urls import path

from .views import EventRetrieveAPIView, EventListAPIView, InterestsFilterEventAPIView, EventFavoriteAPIView


urlpatterns = [
    path("", EventListAPIView.as_view()),
    path("<int:pk>/", EventRetrieveAPIView.as_view()),
    path("filter_interest/", InterestsFilterEventAPIView.as_view()),
    path('api_favorite/', EventFavoriteAPIView.as_view({'get': 'list'})),

]
