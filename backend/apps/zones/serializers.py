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

    latitude = serializers.DecimalField(max_digits=10, decimal_places=7)

    longitude = serializers.DecimalField(max_digits=10, decimal_places=7)


class ZoneSerializer(serializers.ModelSerializer):
    region_nom = serializers.CharField(source="region.nom", read_only=True)

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

        department_query = Department.objects.select_related("region")
        if department_name:
            department_query = department_query.filter(nom__iexact=department_name)
        if region_name:
            department_query = department_query.filter(region__nom__iexact=region_name)
        department = department_query.filter(geometrie__contains=location).first()
        if department is None and department_name:
            department = department_query.first()
        if department is None:
            raise serializers.ValidationError({
                "departement": "Sélectionnez un département valide correspondant au point choisi."
            })
        if region_name and department.region.nom.casefold() != region_name.casefold():
            raise serializers.ValidationError({
                "region": "Le département sélectionné n'appartient pas à cette région."
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
