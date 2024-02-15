from django.urls import path

from .views import *


urlpatterns = [
    path('permanent_notification/', PermanentNotificationAPIView.as_view()),
    path('temporary_notification/', TemporaryNotificationAPIView.as_view())
]
