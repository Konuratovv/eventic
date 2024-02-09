from django.urls import path

from apps.questions.views import QuestionsListAPIView

urlpatterns = [
    path('questions/', QuestionsListAPIView.as_view()),
]