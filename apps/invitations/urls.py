from django.urls import path 
from rest_framework.routers import DefaultRouter

from apps.invitations.views import InvitationAPIViewSet

router = DefaultRouter()
router.register('invitations', InvitationAPIViewSet, "api_invitations")


urlpatterns = router.urls
