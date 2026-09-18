from django.urls import path

from .views import (
    BailleurDetailView, BailleurListCreateView, BudgetDetailView, BudgetListCreateView,
    DepenseDetailView, DepenseListCreateView, DepenseStatusView, DonDetailView,
    DonListCreateView, FinanceDashboardView, JustificatifDetailView,
    JustificatifListCreateView, PartenaireDetailView, PartenaireListCreateView,
    PosteDetailView, PosteListCreateView,
)

urlpatterns = [
    path("bailleurs/", BailleurListCreateView.as_view()),
    path("bailleurs/<uuid:id>/", BailleurDetailView.as_view()),
    path("partenaires/", PartenaireListCreateView.as_view()),
    path("partenaires/<uuid:id>/", PartenaireDetailView.as_view()),
    path("dons/", DonListCreateView.as_view()),
    path("dons/<uuid:id>/", DonDetailView.as_view()),
    path("budgets/", BudgetListCreateView.as_view()),
    path("budgets/<uuid:id>/", BudgetDetailView.as_view()),
    path("budgets/<uuid:budget_id>/postes/", PosteListCreateView.as_view()),
    path("postes/<uuid:id>/", PosteDetailView.as_view()),
    path("depenses/", DepenseListCreateView.as_view()),
    path("depenses/<uuid:id>/", DepenseDetailView.as_view()),
    path("depenses/<uuid:id>/statut/", DepenseStatusView.as_view()),
    path("depenses/<uuid:depense_id>/justificatifs/", JustificatifListCreateView.as_view()),
    path("justificatifs/<int:id>/", JustificatifDetailView.as_view()),
    path("dashboard/finance/", FinanceDashboardView.as_view()),
]