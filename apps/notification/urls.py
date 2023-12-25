from django.urls import path
from .views import NotificationsAPIViewSet

urlpatterns = [
    path('noti/', NotificationsAPIViewSet.as_view({'get': 'list', 'post': 'create'}), name='noti'),
    # Добавьте другие маршруты, если необходимо
]
