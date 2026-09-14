from rest_framework import serializers

from .models import Zone, Region, Department


class RegionSerializer(serializers.ModelSerializer):

    class Meta:
        model = Region
        fields = "__all__"


class DepartmentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Department
        fields = "__all__"


class ReverseGeocodeSerializer(serializers.Serializer):

    latitude = serializers.DecimalField(max_digits=10, decimal_places=7)

    longitude = serializers.DecimalField(max_digits=10, decimal_places=7)


class ReverseGeocodeResponseSerializer(serializers.Serializer):

    region = serializers.CharField()

    departement = serializers.CharField()

    latitude = serializers.DecimalField(max_digits=10, decimal_places=7)

    longitude = serializers.DecimalField(max_digits=10, decimal_places=7)


class ZoneSerializer(serializers.ModelSerializer):

    class Meta:
        model = Zone
        fields = [
            "id",
            "nom",
            "region",
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
            "latitude",
            "longitude",
            "location",
            "region",
            "departement",
            "created_by",
            "created_at",
            "updated_at",
        ]


class ZoneCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Zone
        fields = [
            "nom",
            "latitude",
            "longitude",
            "rayon",
            "statut",
        ]

    def validate_nom(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("Le nom de la zone est obligatoire.")
        return value

    def validate_rayon(self, value):
        if not value or value <= 0:
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
