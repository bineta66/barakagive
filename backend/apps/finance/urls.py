from django.urls import path

from .views import (
    BudgetAnalysisView, BudgetDetailView, BudgetListCreateView, DashboardView,
    DepenseDetailView, DepenseListCreateView, DonDetailView, DonListCreateView,
    JustificationDetailView, JustificationListCreateView,
)

urlpatterns = [
    path("dashboard/", DashboardView.as_view()),
    path("budgets/", BudgetListCreateView.as_view()),
    path("budgets/<uuid:id>/", BudgetDetailView.as_view()),
    path("budget-analysis/<uuid:campaign_id>/", BudgetAnalysisView.as_view()),
    path("dons/", DonListCreateView.as_view()),
    path("dons/<uuid:id>/", DonDetailView.as_view()),
    path("depenses/", DepenseListCreateView.as_view()),
    path("depenses/<uuid:id>/", DepenseDetailView.as_view()),
    path("depenses/<uuid:depense_id>/justifications/", JustificationListCreateView.as_view()),
    path("justifications/<uuid:id>/", JustificationDetailView.as_view()),
]