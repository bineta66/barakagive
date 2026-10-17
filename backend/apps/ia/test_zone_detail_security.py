from types import SimpleNamespace
from unittest.mock import Mock, patch
from uuid import uuid4

from django.test import SimpleTestCase
from rest_framework.test import APIRequestFactory, force_authenticate

from apps.ia.views import ZoneDetailView
from apps.zones.models import Zone


class ZoneDetailAuthorizationTests(SimpleTestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.campaign = SimpleNamespace(organization_id=10)
        self.user = SimpleNamespace(
            is_authenticated=True,
            role="GERANT",
            organization_id=10,
        )

    @patch("apps.ia.views.get_zone_beneficiaries_detail")
    @patch("apps.ia.views.IAnalyse.objects.filter")
    @patch("apps.ia.views.zone_is_visible_to_user", return_value=True)
    @patch("apps.ia.views.get_active_campaign")
    @patch("apps.ia.views.Zone.objects.filter")
    @patch("apps.ia.views.Zone.objects.get", side_effect=ValueError)
    def test_zone_name_uses_the_validated_zone_id_for_detail_lookup(
        self,
        _get_zone,
        filter_zones,
        get_campaign,
        _zone_visible,
        analyses,
        get_detail,
    ):
        zone_id = uuid4()
        filter_zones.return_value.first.return_value = SimpleNamespace(
            pk=zone_id,
            nom="Zone de Dakar",
        )
        get_campaign.return_value = self.campaign
        analyses.return_value.first.return_value = None
        get_detail.return_value = {"zone_id": str(zone_id)}
        request = self.factory.get("/api/ia/zones/Zone de Dakar")
        force_authenticate(request, user=self.user)

        response = ZoneDetailView.as_view()(request, id="Zone de Dakar")

        self.assertEqual(response.status_code, 200)
        get_detail.assert_called_once_with(self.campaign, str(zone_id))

    @patch("apps.ia.views.get_active_campaign")
    @patch("apps.ia.views.Zone.objects.filter")
    @patch("apps.ia.views.Zone.objects.get", side_effect=Zone.DoesNotExist)
    def test_zone_from_another_organization_is_not_found(
        self,
        _get_zone,
        filter_zones,
        get_campaign,
    ):
        filter_zones.return_value.first.return_value = None
        get_campaign.return_value = self.campaign
        request = self.factory.get(f"/api/ia/zones/{uuid4()}")
        force_authenticate(request, user=self.user)

        response = ZoneDetailView.as_view()(request, id=str(uuid4()))

        self.assertEqual(response.status_code, 404)
