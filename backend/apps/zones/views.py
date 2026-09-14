from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.gis.geos import Point

from drf_spectacular.utils import extend_schema

from .models import Zone, Region, Department
from .serializers import (
    ZoneSerializer,
    ZoneCreateSerializer,
    ReverseGeocodeSerializer,
    ReverseGeocodeResponseSerializer,
)


@extend_schema(tags=["Zones"])
class ReverseGeocodeView(APIView):

    @extend_schema(tags=["Zones"])
    def post(self, request):
        serializer = ReverseGeocodeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        latitude = serializer.validated_data["latitude"]
        longitude = serializer.validated_data["longitude"]

        point = Point(longitude, latitude, srid=4326)

        department = Department.objects.filter(
            geometrie__contains=point
        ).first()

        if not department:
            return Response(
                {"detail": "Aucune région trouvée pour ces coordonnées."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        response = ReverseGeocodeResponseSerializer({
            "region": department.region.nom,
            "departement": department.nom,
            "latitude": latitude,
            "longitude": longitude,
        })

        return Response(response.data, status=status.HTTP_200_OK)


@extend_schema(tags=["Zones"])
class ZoneListView(generics.ListCreateAPIView):

    serializer_class = ZoneSerializer
    queryset = Zone.objects.select_related(
        "organization", "created_by"
    ).all()

    def get_serializer_class(self):
        if self.request.method == "POST":
            return ZoneCreateSerializer
        return ZoneSerializer

    def perform_create(self, serializer):
        serializer.save(
            created_by=self.request.user,
            organization=self.request.user.organization,
        )


@extend_schema(tags=["Zones"])
class ZoneDetailView(generics.RetrieveUpdateDestroyAPIView):

    serializer_class = ZoneSerializer
    queryset = Zone.objects.select_related(
        "organization", "created_by"
    ).all()

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
