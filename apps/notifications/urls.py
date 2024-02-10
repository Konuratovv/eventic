from django.urls import path

from .views import *


urlpatterns = [
    path('new_events/', Notifications.as_view(),),

]
