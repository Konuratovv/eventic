from rest_framework.generics import RetrieveAPIView, get_object_or_404
from apps.profiles.models import User
from apps.profiles.serializer import ProfileSerializer
from rest_framework.response import Response


class ProfileViewSet(RetrieveAPIView):
    serializer_class = ProfileSerializer

    def retrieve(self, request, *args, **kwargs):
        user = User.objects.get(id=self.request.user.id)
        serializer = self.get_serializer(user)
        return Response(serializer.data)
