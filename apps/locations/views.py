from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from apps.locations.models import City
from apps.locations.serializers import CitySerializer


class CityListAPIView(generics.ListAPIView):
    queryset = City.objects.all()
    serializer_class = CitySerializer
    permission_classes = [IsAuthenticated]
