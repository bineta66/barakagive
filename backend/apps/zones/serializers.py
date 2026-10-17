from decimal import Decimal, InvalidOperation

from rest_framework import serializers
from django.contrib.gis.geos import Point

from .models import Zone, Region, Department


class RegionSerializer(serializers.ModelSerializer):

    class Meta:
        model = Region
        fields = ["id", "nom"]


class DepartmentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Department
        fields = "__all__"


class ReverseGeocodeSerializer(serializers.Serializer):

    latitude = serializers.DecimalField(
        max_digits=10, decimal_places=7,
        min_value=Decimal("-90"), max_value=Decimal("90"),
    )

    longitude = serializers.DecimalField(
        max_digits=10, decimal_places=7,
        min_value=Decimal("-180"), max_value=Decimal("180"),
    )


class ReverseGeocodeResponseSerializer(serializers.Serializer):

    region = serializers.CharField()

    departement = serializers.CharField()

    departements = serializers.ListField(child=serializers.CharField(), required=False)

    latitude = serializers.DecimalField(max_digits=10, decimal_places=7)

    longitude = serializers.DecimalField(max_digits=10, decimal_places=7)


class ZoneSerializer(serializers.ModelSerializer):
    region_nom = serializers.CharField(source="region.nom", read_only=True)
    departement_nom = serializers.CharField(source="departement.nom", read_only=True)

    def to_internal_value(self, data):
        data = data.copy() if hasattr(data, "copy") else dict(data)
        raw_region = data.get("region")

        if isinstance(raw_region, str) and raw_region.strip() and not raw_region.strip().isdigit():
            region = Region.objects.filter(nom__iexact=raw_region.strip()).first()
            if region is not None:
                data["region"] = region.pk
                raw_latitude = data.get("latitude", getattr(self.instance, "latitude", None))
                raw_longitude = data.get("longitude", getattr(self.instance, "longitude", None))
                try:
                    latitude = Decimal(str(raw_latitude))
                    longitude = Decimal(str(raw_longitude))
                    if (
                        latitude.is_finite()
                        and longitude.is_finite()
                        and Decimal("-90") <= latitude <= Decimal("90")
                        and Decimal("-180") <= longitude <= Decimal("180")
                    ):
                        point = Point(float(longitude), float(latitude), srid=4326)
                        department = Department.objects.filter(
                            region=region,
                            geometrie__contains=point,
                        ).first()
                        if department is not None:
                            data["departement"] = department.pk
                except (InvalidOperation, TypeError, ValueError):
                    pass

        raw_dept = data.get("departement")
        if isinstance(raw_dept, str) and raw_dept.strip() and not raw_dept.strip().isdigit():
            reg_id = data.get("region")
            reg_obj = Region.objects.filter(pk=reg_id).first() if reg_id else None
            if reg_obj:
                dept_obj = Department.objects.filter(nom__iexact=raw_dept.strip(), region=reg_obj).first()
                if not dept_obj:
                    dept_obj, _ = Department.objects.get_or_create(
                        nom=raw_dept.strip(),
                        region=reg_obj,
                        defaults={"geometrie": reg_obj.geometrie},
                    )
                if dept_obj:
                    data["departement"] = dept_obj.pk

        return super().to_internal_value(data)

    def validate_nom(self, value):
        value = (value or "").strip()
        if not value:
            raise serializers.ValidationError("Le nom de la zone est obligatoire.")
        return value

    def validate_rayon(self, value):
        if value is None or value <= 0:
            raise serializers.ValidationError("Le rayon doit être supérieur à 0.")
        return value

    def validate_latitude(self, value):
        if not Decimal("-90") <= value <= Decimal("90"):
            raise serializers.ValidationError("La latitude doit être entre -90 et 90.")
        return value

    def validate_longitude(self, value):
        if not Decimal("-180") <= value <= Decimal("180"):
            raise serializers.ValidationError("La longitude doit être entre -180 et 180.")
        return value

    class Meta:
        model = Zone
        fields = [
            "id",
            "nom",
            "region",
            "region_nom",
            "departement",
            "departement_nom",
            "latitude",
            "longitude",
            "location",
            "rayon",
            "statut",
            "organization",
            "created_by",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "location",
            "created_by",
            "organization",
            "created_at",
            "updated_at",
        ]

    def update(self, instance, validated_data):
        latitude = validated_data.get("latitude", instance.latitude)
        longitude = validated_data.get("longitude", instance.longitude)
        validated_data["location"] = Point(float(longitude), float(latitude), srid=4326)
        return super().update(instance, validated_data)

    def validate(self, attrs):
        region = attrs.get("region", getattr(self.instance, "region", None))
        department = attrs.get("departement", getattr(self.instance, "departement", None))
        if region and department and department.region_id != region.pk:
            raise serializers.ValidationError({
                "departement": "Le département doit appartenir à la région sélectionnée."
            })
        return attrs


class ZoneCreateSerializer(serializers.ModelSerializer):
    region = serializers.CharField(required=False, max_length=100)
    departement = serializers.CharField(required=False, max_length=100)

    class Meta:
        model = Zone
        fields = [
            "nom",
            "region",
            "departement",
            "latitude",
            "longitude",
            "rayon",
            "statut",
        ]

    def create(self, validated_data):
        from django.contrib.gis.geos import Point
        lat = float(validated_data["latitude"])
        lng = float(validated_data["longitude"])
        location = Point(lng, lat, srid=4326)
        region_name = (validated_data.pop("region", "") or "").strip()
        department_name = (validated_data.pop("departement", "") or "").strip()

        department = None

        # 1. Try exact spatial match: department whose geometry contains the point
        dept_qs = Department.objects.select_related("region").filter(geometrie__contains=location)
        if region_name:
            dept_qs = dept_qs.filter(region__nom__iexact=region_name)
        department = dept_qs.first()

        # 2. Fallback: find department by name (ignore geometry)
        if department is None and department_name:
            dept_qs2 = Department.objects.select_related("region").filter(nom__iexact=department_name)
            if region_name:
                dept_qs2 = dept_qs2.filter(region__nom__iexact=region_name)
            department = dept_qs2.first()

        # 3. Match or create for the specified region
        if department is None and region_name:
            from django.contrib.gis.geos import GEOSGeometry
            default_geom = GEOSGeometry("POLYGON((0 0, 0 1, 1 1, 1 0, 0 0))", srid=4326)
            region_obj = Region.objects.filter(nom__iexact=region_name).first()
            if not region_obj:
                region_obj, _ = Region.objects.get_or_create(
                    nom=region_name,
                    defaults={"geometrie": default_geom},
                )
            target_dept_name = department_name if department_name else region_obj.nom
            department = Department.objects.filter(nom__iexact=target_dept_name, region=region_obj).first()
            if department is None:
                department, _ = Department.objects.get_or_create(
                    nom=target_dept_name,
                    region=region_obj,
                    defaults={"geometrie": region_obj.geometrie or default_geom},
                )

        # 4. Try any department in DB whose region geometry contains the point
        if department is None:
            region_by_geom = Region.objects.filter(geometrie__contains=location).first()
            if region_by_geom:
                target_dept_name = department_name if department_name else region_by_geom.nom
                department = Department.objects.filter(nom__iexact=target_dept_name, region=region_by_geom).first()
                if department is None:
                    department, _ = Department.objects.get_or_create(
                        nom=target_dept_name,
                        region=region_by_geom,
                        defaults={"geometrie": region_by_geom.geometrie},
                    )

        if department is None:
            raise serializers.ValidationError({
                "departement": (
                    "Aucune région reconnue pour ce point. "
                    "Assurez-vous de cliquer dans les limites du Sénégal."
                )
            })

        validated_data["region"] = department.region
        validated_data["departement"] = department
        validated_data["location"] = location
        return super().create(validated_data)

    def validate_nom(self, value):
        value = (value or "").strip()
        if not value:
            raise serializers.ValidationError("Le nom de la zone est obligatoire.")
        if len(value) > 200:
            raise serializers.ValidationError("Le nom de la zone ne peut pas dépasser 200 caractères.")
        return value

    def validate_rayon(self, value):
        if value is None or value <= 0:
            raise serializers.ValidationError("Le rayon doit être supérieur à 0.")
        return value

    def validate_latitude(self, value):
        if value < -90 or value > 90:
            raise serializers.ValidationError("La latitude doit être entre -90 et 90.")
        return value

    def validate_longitude(self, value):
        if value < -180 or value > 180:
            raise serializers.ValidationError("La longitude doit être entre -180 et 180.")
        return value
