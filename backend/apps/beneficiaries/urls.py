from django.urls import path

from .views import (
    BeneficiaryListCreateView,
    BeneficiaryDetailView,
    BeneficiarySyncView,
    BeneficiaryAIScoreView,
)

urlpatterns = [
    path("", BeneficiaryListCreateView.as_view(), name="beneficiary-list-create"),
    path("sync/", BeneficiarySyncView.as_view(), name="beneficiary-sync"),
    path("<uuid:pk>/", BeneficiaryDetailView.as_view(), name="beneficiary-detail"),
    path("<uuid:pk>/ai-score/", BeneficiaryAIScoreView.as_view(), name="beneficiary-ai-score"),
]