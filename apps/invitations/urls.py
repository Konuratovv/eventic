from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import NotificationsAPIViewSet

router = DefaultRouter()
router.register(r'invi', NotificationsAPIViewSet, basename='noti')

urlpatterns = [
    path('', include(router.urls)),
    # Добавьте другие маршруты, если необходимо
]
