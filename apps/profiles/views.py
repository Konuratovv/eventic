from rest_framework import status
from rest_framework.generics import RetrieveAPIView, get_object_or_404, ListCreateAPIView
from apps.profiles.models import User, Organizer
from apps.profiles.serializer import ProfileSerializer, OrganizerSerializer, FollowSerializer
from rest_framework.response import Response
from rest_framework.permissions import AllowAny


class ProfileViewSet(RetrieveAPIView):
    serializer_class = ProfileSerializer

    def retrieve(self, request, *args, **kwargs):
        user = User.objects.get(id=self.request.user.id)
        serializer = self.get_serializer(user)
        return Response(serializer.data)


class FollowAPIView(ListCreateAPIView):
    queryset = Organizer.objects.all()
    permission_classes = [AllowAny]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return FollowSerializer
        else:
            return OrganizerSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Followed'})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
