from django.urls import path

from .views import (
    ProjectListCreateView,
    ProjectDetailView,
    ProjectBudgetView,
    ProjectCriteriaListView,
    ProjectCriteriaDetailView,
    ProjectDecisionDashboardView,
    ProjectDashboardAssistantChatView,
    ProjectCampaignProposalView,
)

app_name = "projects"

urlpatterns = [
    path("projects/dashboard/", ProjectDecisionDashboardView.as_view(), name="project-decision-dashboard"),
    path("projects/dashboard/chat/", ProjectDashboardAssistantChatView.as_view(), name="project-dashboard-assistant-chat"),
    path("projects/<int:project_id>/campaign-proposals/", ProjectCampaignProposalView.as_view(), name="project-campaign-proposals"),
    path("projects/", ProjectListCreateView.as_view(), name="project-list"),
    path("projects/<int:pk>/", ProjectDetailView.as_view(), name="project-detail"),
    path("projects/<int:pk>/budget/", ProjectBudgetView.as_view(), name="project-budget"),
    path("projets/<int:project_id>/criteres/", ProjectCriteriaListView.as_view(), name="project-criteria-list"),
    path("criteres/<int:pk>/", ProjectCriteriaDetailView.as_view(), name="criteria-detail"),
]
