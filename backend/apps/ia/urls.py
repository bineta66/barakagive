from django.urls import path
from .views import (
    ExecutiveInsightView,
    RegionZonesView,
    ZoneDetailView,
    BudgetAnalysisView,
)

urlpatterns = [
    path('executive-insight', ExecutiveInsightView.as_view(), name='executive_insight'),
    path('regions/<str:id>/zones', RegionZonesView.as_view(), name='region_zones'),
    path('zones/<str:id>', ZoneDetailView.as_view(), name='zone_detail'),
    path('budget-analysis/<str:campagne_id>', BudgetAnalysisView.as_view(), name='budget_analysis'),
]