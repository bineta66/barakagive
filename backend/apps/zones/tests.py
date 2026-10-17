from types import SimpleNamespace
from unittest.mock import Mock, patch
from datetime import date

from django.contrib.gis.geos import Point, Polygon
from django.test import SimpleTestCase, TestCase
from rest_framework.exceptions import ValidationError
from rest_framework.test import APIClient

from apps.accounts.models import User
from apps.campaigns.models import Campaign
from apps.organizations.models import Organization
from apps.projects.models import Project
from .models import Department, Region, Zone

from .serializers import ZoneCreateSerializer, ZoneSerializer


class ZoneFormPayloadValidationTests(SimpleTestCase):
    def test_create_rejects_blank_name_and_invalid_numeric_values(self):
        for payload, field in (
            ({"nom": "   ", "latitude": 14, "longitude": -17, "rayon": 1}, "nom"),
            ({"nom": "Zone valide", "latitude": 91, "longitude": -17, "rayon": 1}, "latitude"),
            ({"nom": "Zone valide", "latitude": 14, "longitude": 181, "rayon": 1}, "longitude"),
            ({"nom": "Zone valide", "latitude": 14, "longitude": -17, "rayon": 0}, "rayon"),
        ):
            with self.subTest(field=field, payload=payload):
                serializer = ZoneCreateSerializer(data=payload)
                self.assertFalse(serializer.is_valid())
                self.assertIn(field, serializer.errors)

    def test_zone_update_rejects_department_from_another_region(self):
        region = SimpleNamespace(pk=1, id=1)
        other_region = SimpleNamespace(pk=2, id=2)
        instance = SimpleNamespace(
            region=region,
            departement=SimpleNamespace(region_id=2, region=other_region),
        )
        serializer = ZoneSerializer(instance=instance)
        with self.assertRaises(ValidationError):
            serializer.validate({})

    def test_zone_update_rejects_out_of_range_coordinates_and_nonpositive_radius(self):
        instance = SimpleNamespace(
            latitude=14, longitude=-17, rayon=100, nom="Zone existante",
            region=None, departement=None,
        )
        for payload, field in (({"latitude": 91}, "latitude"), ({"rayon": -1}, "rayon")):
            with self.subTest(field=field):
                serializer = ZoneSerializer(instance=instance, data=payload, partial=True)
                self.assertFalse(serializer.is_valid())
                self.assertIn(field, serializer.errors)

    @patch("apps.zones.serializers.Department.objects.filter")
    @patch("apps.zones.serializers.Region.objects.filter")
    def test_zone_update_resolves_map_names_to_geographic_relations(
        self, region_filter, department_filter
    ):
        region = SimpleNamespace(pk=1)
        department = SimpleNamespace(pk=2, region_id=1, region=region)
        region_filter.return_value.first.return_value = region
        department_filter.return_value.first.return_value = department

        instance = SimpleNamespace(
            latitude=14,
            longitude=-17,
            rayon=100,
            region=region,
            departement=department,
        )
        serializer = ZoneSerializer(
            instance=instance,
            data={
                "region": "Dakar",
                "departement": "Dakar",
                "latitude": "14.7000000",
                "longitude": "-17.4000000",
            },
            partial=True,
        )
        serializer.fields["region"].queryset = Mock()
        serializer.fields["region"].queryset.get.return_value = region
        serializer.fields["departement"].queryset = Mock()
        serializer.fields["departement"].queryset.get.return_value = department

        self.assertTrue(serializer.is_valid(), serializer.errors)
        self.assertIs(serializer.validated_data["region"], region)
        self.assertIs(serializer.validated_data["departement"], department)

    def test_organization_cannot_be_changed_through_zone_serializer(self):
        self.assertTrue(ZoneSerializer().fields["organization"].read_only)


class ZoneSearchIsolationTests(TestCase):
    def setUp(self):
        self.organization = Organization.objects.create(
            name="ONG Zone Search",
            email="zone-search@example.test",
            phone="771234569",
            address="Dakar",
            region="Dakar",
            country="Senegal",
            intervention_domain="Humanitaire",
        )
        self.chef = User.objects.create_user(
            email="zone-search-chef@example.test",
            password="SafePass123!",
            role=User.Role.CHEF_PROJET,
            status=User.Status.ACTIVE,
            is_active=True,
            organization=self.organization,
        )
        self.project = Project.objects.create(
            name="Projet zones",
            description="",
            region="Dakar",
            objectif="Test",
            start_date=date(2026, 1, 1),
            end_date=date(2026, 12, 31),
            chef_projet=self.chef,
            responsable_finance=self.chef,
            organization=self.organization,
            created_by=self.chef,
        )
        polygon = Polygon(((-18, 12), (-16, 12), (-16, 15), (-18, 15), (-18, 12)), srid=4326)
        self.region = Region.objects.create(nom="Dakar Zone Search", geometrie=polygon)
        department = Department.objects.create(
            nom="Dakar Zone Search", region=self.region, geometrie=polygon,
        )
        self.zone = Zone.objects.create(
            nom="Zone autorisée",
            region=self.region,
            departement=department,
            latitude=14.7,
            longitude=-17.4,
            location=Point(-17.4, 14.7, srid=4326),
            rayon=1000,
            organization=self.organization,
            created_by=self.chef,
        )
        self.campaign = Campaign.objects.create(
            projet=self.project,
            organization=self.organization,
            nom="Campagne zones",
            code_campagne="ZONE-SEARCH-1",
            description="Test",
            date_debut=date(2026, 10, 1),
            date_fin=date(2026, 10, 2),
            created_by=self.chef,
        )
        self.campaign.zones.add(self.zone)
        self.client = APIClient()
        self.client.force_authenticate(self.chef)

    def test_search_by_ids_returns_only_zones_attached_to_chef_campaigns(self):
        unassigned = Zone.objects.create(
            nom="Zone non affectée",
            region=self.region,
            departement=self.zone.departement,
            latitude=14.8,
            longitude=-17.3,
            location=Point(-17.3, 14.8, srid=4326),
            rayon=1000,
            organization=self.organization,
            created_by=self.chef,
        )
        allowed = self.client.get(
            f"/api/zones/?ids={self.zone.pk}&page=1&page_size=20"
        )
        self.assertEqual(allowed.status_code, 200)
        self.assertEqual(allowed.data["count"], 1)
        self.assertEqual(allowed.data["results"][0]["region_nom"], self.region.nom)

        denied = self.client.get(
            f"/api/zones/?ids={unassigned.pk}&page=1&page_size=20"
        )
        self.assertEqual(denied.status_code, 200)
        self.assertEqual(denied.data["count"], 0)
