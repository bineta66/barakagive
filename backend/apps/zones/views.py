from rest_framework import generics, status
import uuid
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import BasePermission, IsAuthenticated
from django.contrib.gis.geos import Point

from drf_spectacular.utils import extend_schema

from .models import Zone, Region, Department
from apps.accounts.permissions import IsAccountActive
from apps.campaigns.models import CampagneAffectation
from apps.common.pagination import StandardPagination
from .serializers import (
    ZoneSerializer,
    ZoneCreateSerializer,
    RegionSerializer,
    ReverseGeocodeSerializer,
    ReverseGeocodeResponseSerializer,
)


class CanManageZones(BasePermission):
    message = "Vous n'avez pas les droits nécessaires pour modifier les zones."

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in {
            "GERANT", "CHEF_PROJET",
        }


@extend_schema(tags=["Zones"])
class ReverseGeocodeView(APIView):
    permission_classes = [IsAuthenticated, IsAccountActive]

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


REGIONS_SENEGAL = [
    "Dakar",
    "Diourbel",
    "Fatick",
    "Kaffrine",
    "Kaolack",
    "Kédougou",
    "Kolda",
    "Louga",
    "Matam",
    "Saint-Louis",
    "Sédhiou",
    "Tambacounda",
    "Thiès",
    "Ziguinchor",
]


@extend_schema(tags=["Zones"])
class ZoneListView(generics.ListCreateAPIView):

    serializer_class = ZoneSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = None
    queryset = Zone.objects.select_related(
        "organization", "created_by"
    ).all()

    def get_serializer_class(self):
        if self.request.method == "POST":
            return ZoneCreateSerializer
        return ZoneSerializer

    def get_permissions(self):
        permissions = [IsAuthenticated(), IsAccountActive()]
        if self.request.method == "POST":
            permissions.append(CanManageZones())
        return permissions

    def get_queryset(self):
        user = self.request.user
        if user.role == "SUPER_ADMIN":
            queryset = self.queryset.all()
        elif not user.organization_id:
            return self.queryset.none()
        elif user.role == "GERANT":
            queryset = self.queryset.filter(organization=user.organization)
        elif user.role == "CHEF_PROJET":
            queryset = self.queryset.filter(
                organization_id=user.organization_id,
                campaigns__projet__chef_projet=user,
                campaigns__organization_id=user.organization_id,
                campaigns__projet__organization_id=user.organization_id,
            )
        elif user.role == "FINANCE":
            queryset = self.queryset.filter(
                organization_id=user.organization_id,
                campaigns__projet__responsable_finance=user,
                campaigns__organization_id=user.organization_id,
                campaigns__projet__organization_id=user.organization_id,
            )
        elif user.role == "AGENT":
            assigned_zone_names = CampagneAffectation.objects.filter(
                agent=user,
                campagne__organization_id=user.organization_id,
            ).values("zone")
            queryset = self.queryset.filter(
                organization_id=user.organization_id,
                nom__in=assigned_zone_names,
            )
        else:
            return self.queryset.none()

        search = (self.request.query_params.get("search") or "").strip()
        if search:
            queryset = queryset.filter(nom__icontains=search)
        raw_ids = (self.request.query_params.get("ids") or "").strip()
        if raw_ids:
            valid_ids = []
            for value in raw_ids.split(",")[:100]:
                try:
                    valid_ids.append(uuid.UUID(value.strip()))
                except (TypeError, ValueError, AttributeError):
                    continue
            queryset = queryset.filter(pk__in=valid_ids)
        return queryset.distinct().order_by("nom", "pk")

    def paginate_queryset(self, queryset):
        # Keep the existing unpaginated response for maps and legacy selectors.
        # Search/autocomplete callers opt into a bounded DRF page explicitly.
        if not (self.request.query_params.get("search") or self.request.query_params.get("page")):
            return None
        if not hasattr(self, "_search_paginator"):
            self._search_paginator = StandardPagination()
        return self._search_paginator.paginate_queryset(queryset, self.request, view=self)

    def get_paginated_response(self, data):
        return self._search_paginator.get_paginated_response(data)

    def perform_create(self, serializer):
        serializer.save(
            created_by=self.request.user,
            organization=self.request.user.organization,
        )


@extend_schema(tags=["Zones"])
class ZoneDetailView(generics.RetrieveUpdateDestroyAPIView):

    serializer_class = ZoneSerializer
    permission_classes = [IsAuthenticated]
    lookup_url_kwarg = "id"
    queryset = Zone.objects.select_related(
        "organization", "created_by"
    ).all()

    def get_permissions(self):
        permissions = [IsAuthenticated(), IsAccountActive()]
        if self.request.method in {"PUT", "PATCH", "DELETE"}:
            permissions.append(CanManageZones())
        return permissions

    def get_queryset(self):
        user = self.request.user
        if user.role == "SUPER_ADMIN":
            return self.queryset.all()
        if not user.organization_id:
            return self.queryset.none()
        if user.role == "GERANT":
            return self.queryset.filter(organization=user.organization)
        if user.role == "CHEF_PROJET":
            return self.queryset.filter(
                organization_id=user.organization_id,
                campaigns__projet__chef_projet=user,
                campaigns__organization_id=user.organization_id,
                campaigns__projet__organization_id=user.organization_id,
            ).distinct()
        if user.role == "FINANCE":
            return self.queryset.filter(
                organization_id=user.organization_id,
                campaigns__projet__responsable_finance=user,
                campaigns__organization_id=user.organization_id,
                campaigns__projet__organization_id=user.organization_id,
            ).distinct()
        if user.role == "AGENT":
            assigned_zone_names = CampagneAffectation.objects.filter(
                agent=user,
                campagne__organization_id=user.organization_id,
            ).values("zone")
            return self.queryset.filter(
                organization_id=user.organization_id,
                nom__in=assigned_zone_names,
            ).distinct()
        return self.queryset.none()

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@extend_schema(tags=["Zones"])
class RegionListView(generics.ListAPIView):
    """GET /api/regions/ — retourne toutes les régions (id + nom)"""
    serializer_class = RegionSerializer
    permission_classes = [IsAuthenticated, IsAccountActive]
    pagination_class = None

    def get_queryset(self):
        # Auto-seed les 14 régions du Sénégal si la table est vide
        # The global geography catalog must not be mutated by a read request.
        return Region.objects.all().order_by("nom")
