from django.urls import path

from .views import (
    BeneficiaryListCreateView,
    BeneficiaryDetailView,
    BeneficiarySyncView,
    BeneficiaryAIScoreView,
    ZoneRankingView,
)

urlpatterns = [
    path("", BeneficiaryListCreateView.as_view(), name="beneficiary-list-create"),
    path("sync/", BeneficiarySyncView.as_view(), name="beneficiary-sync"),
    path("<uuid:pk>/", BeneficiaryDetailView.as_view(), name="beneficiary-detail"),
    path("<uuid:pk>/ai-score/", BeneficiaryAIScoreView.as_view(), name="beneficiary-ai-score"),
    path("zone-ranking/", ZoneRankingView.as_view(), name="beneficiary-zone-ranking"),
]
