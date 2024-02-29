from rest_framework import generics

from apps.questions.models import Question
from apps.questions.serializers import QuestionSerializer


# Create your views here.

class QuestionsListAPIView(generics.ListAPIView):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer
