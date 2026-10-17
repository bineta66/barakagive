from rest_framework import generics, status
import uuid
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import BasePermission, IsAuthenticated
from django.db.models import Q
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


import json
import os
import math

SENEGAL_REGIONS_DEPARTEMENTS = {
    "Dakar": ["Dakar", "Guédiawaye", "Keur Massar", "Pikine", "Rufisque"],
    "Diourbel": ["Bambey", "Diourbel", "Mbacké"],
    "Fatick": ["Fatick", "Foundiougne", "Gossas"],
    "Kaffrine": ["Birkelane", "Kaffrine", "Koungheul", "Malem Hodar"],
    "Kaolack": ["Guinguinéo", "Kaolack", "Nioro du Rip"],
    "Kédougou": ["Kédougou", "Salémata", "Saraya"],
    "Kolda": ["Kolda", "Médina Yoro Foulah", "Vélingara"],
    "Louga": ["Kébémer", "Linguère", "Louga"],
    "Matam": ["Kanel", "Matam", "Ranérou"],
    "Saint-Louis": ["Dagana", "Podor", "Saint-Louis"],
    "Sédhiou": ["Bounkiling", "Goudomp", "Sédhiou"],
    "Tambacounda": ["Bakel", "Goudiry", "Koumpentoum", "Tambacounda"],
    "Thiès": ["Mbour", "Thiès", "Tivaouane"],
    "Ziguinchor": ["Bignona", "Oussouye", "Ziguinchor"],
}

def _point_in_polygon_raycast(x, y, poly):
    n = len(poly)
    if n < 3:
        return False
    inside = False
    p1x, p1y = poly[0]
    for i in range(1, n + 1):
        p2x, p2y = poly[i % n]
        if y > min(p1y, p2y):
            if y <= max(p1y, p2y):
                if x <= max(p1x, p2x):
                    if p1y != p2y:
                        xinters = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                    if p1x == p2x or x <= xinters:
                        inside = not inside
        p1x, p1y = p2x, p2y
    return inside

def _point_in_geojson_geom(x, y, geom):
    g_type = geom.get("type")
    coords = geom.get("coordinates", [])
    if g_type == "Polygon":
        if coords and _point_in_polygon_raycast(x, y, coords[0]):
            return True
    elif g_type == "MultiPolygon":
        for poly in coords:
            if poly and _point_in_polygon_raycast(x, y, poly[0]):
                return True
    return False

def _centroid_of_coords(coords):
    total_x = 0.0
    total_y = 0.0
    count = 0
    def _accum(c):
        nonlocal total_x, total_y, count
        if isinstance(c[0], (int, float)):
            total_x += c[0]
            total_y += c[1]
            count += 1
        else:
            for sub in c:
                _accum(sub)
    _accum(coords)
    return (total_x / count, total_y / count) if count > 0 else (0.0, 0.0)

_GEOJSON_FEATURES = None

def _load_senegal_geojson():
    global _GEOJSON_FEATURES
    if _GEOJSON_FEATURES is not None:
        return _GEOJSON_FEATURES
    _GEOJSON_FEATURES = []
    
    path = os.path.join(os.path.dirname(__file__), "data", "senegal-regions.geojson")
    if not os.path.exists(path):
        path = os.path.join(os.path.dirname(__file__), "..", "..", "..", "frontend", "src", "data", "senegal-regions.geojson")
    
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
                for feat in data.get("features", []):
                    props = feat.get("properties", {})
                    name = props.get("shapeName") or props.get("name")
                    geom = feat.get("geometry")
                    if name and geom:
                        centroid = _centroid_of_coords(geom.get("coordinates", []))
                        geos_geom = None
                        try:
                            from django.contrib.gis.geos import GEOSGeometry
                            geos_geom = GEOSGeometry(json.dumps(geom), srid=4326)
                        except Exception:
                            pass
                        _GEOJSON_FEATURES.append({
                            "name": name,
                            "geom": geom,
                            "geos_geom": geos_geom,
                            "centroid": centroid,
                        })
        except Exception:
            pass
    return _GEOJSON_FEATURES

def find_region_for_coordinates(longitude, latitude, geos_point=None):
    features = _load_senegal_geojson()
    if not features:
        return None

    # 1. Exact match via GEOS if available
    if geos_point:
        for item in features:
            if item.get("geos_geom"):
                try:
                    if item["geos_geom"].contains(geos_point):
                        return item["name"]
                except Exception:
                    pass

    # 2. Match via pure Python raycasting
    for item in features:
        if _point_in_geojson_geom(longitude, latitude, item["geom"]):
            return item["name"]

    # 3. Fallback: closest region centroid
    best_name = None
    min_dist = float("inf")
    for item in features:
        cx, cy = item["centroid"]
        dist = math.hypot(longitude - cx, latitude - cy)
        if dist < min_dist:
            min_dist = dist
            best_name = item["name"]

    return best_name


@extend_schema(tags=["Zones"])
class ReverseGeocodeView(APIView):
    permission_classes = [IsAuthenticated, IsAccountActive]

    @extend_schema(tags=["Zones"])
    def post(self, request):
        serializer = ReverseGeocodeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        latitude = serializer.validated_data["latitude"]
        longitude = serializer.validated_data["longitude"]

        point = Point(float(longitude), float(latitude), srid=4326)

        region_name = None
        dept_name = None

        # 1. Try exact department geometry match first
        department = Department.objects.select_related("region").filter(
            geometrie__contains=point
        ).first()

        if department:
            region_name = department.region.nom
            dept_name = department.nom
        else:
            # 2. Try match by region geometry in DB
            region = Region.objects.filter(geometrie__contains=point).first()
            if region:
                region_name = region.nom

        # 3. Fallback: match by Senegal GeoJSON boundaries
        if not region_name:
            region_name = find_region_for_coordinates(float(longitude), float(latitude), point)

        # 4. Final safety fallback: default to Dakar
        if not region_name:
            region_name = "Dakar"

        available_depts = SENEGAL_REGIONS_DEPARTEMENTS.get(region_name, [region_name])
        if not dept_name or dept_name not in available_depts:
            dept_name = region_name if region_name in available_depts else available_depts[0]

        response = ReverseGeocodeResponseSerializer({
            "region": region_name,
            "departement": dept_name,
            "departements": available_depts,
            "latitude": latitude,
            "longitude": longitude,
        })

        return Response(response.data, status=status.HTTP_200_OK)


@extend_schema(tags=["Zones"])
class DepartmentListView(APIView):
    permission_classes = [IsAuthenticated, IsAccountActive]

    @extend_schema(tags=["Zones"])
    def get(self, request):
        region_name = (request.query_params.get("region") or "").strip()
        if region_name:
            for reg, depts in SENEGAL_REGIONS_DEPARTEMENTS.items():
                if reg.lower() == region_name.lower():
                    return Response([{"nom": d, "region": reg} for d in depts])
            qs = Department.objects.filter(region__nom__iexact=region_name)
            if qs.exists():
                return Response([{"nom": d.nom, "region": d.region.nom} for d in qs])
            return Response([{"nom": region_name, "region": region_name}])

        results = []
        for reg, depts in SENEGAL_REGIONS_DEPARTEMENTS.items():
            for d in depts:
                results.append({"nom": d, "region": reg})
        return Response(results)


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
            ).filter(
                Q(created_by=user)
                | Q(
                    campaigns__projet__chef_projet=user,
                    campaigns__organization_id=user.organization_id,
                    campaigns__projet__organization_id=user.organization_id,
                )
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
            ).filter(
                Q(created_by=user)
                | Q(
                    campaigns__projet__chef_projet=user,
                    campaigns__organization_id=user.organization_id,
                    campaigns__projet__organization_id=user.organization_id,
                )
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
