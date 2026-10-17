from django.urls import path

from .views import (
    FinanceDashboardView,
    BudgetListCreateView,
    BudgetDetailView,
    BudgetApprovalView,
    LigneBudgetaireListCreateView,
    LigneBudgetaireDetailView,
    DonateurListCreateView,
    DonateurDetailView,
    FinancementListCreateView,
    FinancementDetailView,
    DonListCreateView,
    DonDetailView,
    DepenseListCreateView,
    DepenseDetailView,
    JustificationListCreateView,
    JustificationDetailView,
    JustificationDocumentView,
    BudgetAnalysisView,
    BailleurListCreateView,
    BailleurDetailView,
    PartenaireListCreateView,
    PartenaireDetailView,
    FinanceAssistantChatView,
    FinanceAssistantHomeView,
)

urlpatterns = [
    path("justifications/<uuid:id>/document/", JustificationDocumentView.as_view(), name="justification-document"),

    # Tableau de bord financier
    path(
        "dashboard/",
        FinanceDashboardView.as_view(),
        name="finance-dashboard",
    ),

    # Lignes budgétaires
    path("lignes-budgetaires/", LigneBudgetaireListCreateView.as_view(), name="ligne-budgetaire-list"),
    path("lignes-budgetaires/<uuid:id>/", LigneBudgetaireDetailView.as_view(), name="ligne-budgetaire-detail"),

    # Donateurs
    path("donateurs/", DonateurListCreateView.as_view(), name="donateur-list"),
    path("donateurs/<uuid:id>/", DonateurDetailView.as_view(), name="donateur-detail"),

    # Financements
    path("financements/", FinancementListCreateView.as_view(), name="financement-list"),
    path("financements/<uuid:id>/", FinancementDetailView.as_view(), name="financement-detail"),

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
    # Budgets - Approuver (Gérant)
    path(
        "budgets/approval/",
        BudgetApprovalView.as_view(),
        name="budget-approval",
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

    # Bailleurs
    path(
        "bailleurs/",
        BailleurListCreateView.as_view(),
        name="bailleur-list",
    ),
    path(
        "bailleurs/<uuid:id>/",
        BailleurDetailView.as_view(),
        name="bailleur-detail",
    ),

    # Partenaires
    path(
        "partenaires/",
        PartenaireListCreateView.as_view(),
        name="partenaire-list",
    ),
    path(
        "partenaires/<uuid:id>/",
        PartenaireDetailView.as_view(),
        name="partenaire-detail",
    ),

    # Assistant IA Finance
    path(
        "assistant/home/",
        FinanceAssistantHomeView.as_view(),
        name="finance-assistant-home",
    ),
    path(
        "assistant/home",
        FinanceAssistantHomeView.as_view(),
    ),
    path(
        "assistant/chat/",
        FinanceAssistantChatView.as_view(),
        name="finance-assistant-chat",
    ),
    path(
        "assistant/chat",
        FinanceAssistantChatView.as_view(),
    ),
]
