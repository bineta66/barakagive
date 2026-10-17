from django.urls import path

from .views import (
    BeneficiaryListCreateView,
    BeneficiaryDetailView,
    BeneficiarySyncView,
    BeneficiaryPWASyncView,
    BeneficiaryVulnerabilityScoreView,
    BeneficiaryActionListCreateView,
    ZoneRankingView,
    ZoneBeneficiariesTableView,
    CheckDuplicateBeneficiaryView,
)

urlpatterns = [
    path("", BeneficiaryListCreateView.as_view(), name="beneficiary-list-create"),
    path("sync/", BeneficiarySyncView.as_view(), name="beneficiary-sync"),
    path("pwa-sync/", BeneficiaryPWASyncView.as_view(), name="beneficiary-pwa-sync"),
    path("pwa-sync", BeneficiaryPWASyncView.as_view()),
    path("check-duplicate/", CheckDuplicateBeneficiaryView.as_view(), name="beneficiary-check-duplicate"),
    path("check-duplicate", CheckDuplicateBeneficiaryView.as_view()),
    path("zone/<uuid:zone_id>/", ZoneBeneficiariesTableView.as_view(), name="beneficiary-zone-table"),
    path("<uuid:pk>/", BeneficiaryDetailView.as_view(), name="beneficiary-detail"),
    path("<uuid:pk>/vulnerability-score/", BeneficiaryVulnerabilityScoreView.as_view(), name="beneficiary-vulnerability-score"),
    # Legacy URL retained while existing API clients migrate to the métier name.
    path("<uuid:pk>/ai-score/", BeneficiaryVulnerabilityScoreView.as_view(), name="beneficiary-ai-score-legacy"),
    path("<uuid:pk>/actions/", BeneficiaryActionListCreateView.as_view(), name="beneficiary-actions"),
    path("zone-ranking/", ZoneRankingView.as_view(), name="beneficiary-zone-ranking"),
]
