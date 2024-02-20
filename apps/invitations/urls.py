from django.urls import path, include
from apps.invitations.views import * 
from rest_framework import routers

urlpatterns = [
    path('invitation-categories/', CategoryAPIView.as_view()),
    path('invitation-contacts/', ContactAPIView.as_view()),
    path('invitation-contacts/<int:pk>/delete', ContactDeleteAPIView.as_view()),
    path('invitation-images/', ImageAPIView.as_view())
]