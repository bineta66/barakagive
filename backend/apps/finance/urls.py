from django.urls import path

from .views import (
    FinanceDashboardView,
    BudgetListCreateView,
    BudgetDetailView,
    DonListCreateView,
    DonDetailView,
    DepenseListCreateView,
    DepenseDetailView,
    JustificationListCreateView,
    JustificationDetailView,
    BudgetAnalysisView,
)

urlpatterns = [

    # Tableau de bord financier
    path(
        "dashboard/",
        FinanceDashboardView.as_view(),
        name="finance-dashboard",
    ),

    # Budgets
    path(
        "budgets/",
        BudgetListCreateView.as_view(),
        name="budget-list",
    ),
    path(
        "budgets/<uuid:id>/",
        BudgetDetailView.as_view(),
        name="budget-detail",
    ),

    # Dons
    path(
        "dons/",
        DonListCreateView.as_view(),
        name="don-list",
    ),
    path(
        "dons/<uuid:id>/",
        DonDetailView.as_view(),
        name="don-detail",
    ),

    # Dépenses
    path(
        "depenses/",
        DepenseListCreateView.as_view(),
        name="depense-list",
    ),
    path(
        "depenses/<uuid:id>/",
        DepenseDetailView.as_view(),
        name="depense-detail",
    ),

    # Justifications
    path(
        "depenses/<uuid:depense_id>/justifications/",
        JustificationListCreateView.as_view(),
        name="justification-list",
    ),
    path(
        "justifications/<uuid:id>/",
        JustificationDetailView.as_view(),
        name="justification-detail",
    ),

    # Assistant Financier IA
    path(
        "ia/budget-analysis/<uuid:campaign_id>/",
        BudgetAnalysisView.as_view(),
        name="budget-analysis",
    ),
]