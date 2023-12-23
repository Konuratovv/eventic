from django.urls import path

from .views import Notifications

# urlpatterns = [
#     path("unread/", UnreadNotifications.as_view()),
#
# ]

urlpatterns = [
    path('noti/<int:pk>/', Notifications.as_view(),),

]
