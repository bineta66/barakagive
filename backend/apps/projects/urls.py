from django.urls import path

from .views import (
    ProjectListCreateView,
    ProjectDetailView,
    ProjectBudgetView,
    ProjectCriteriaListView,
)

app_name = "projects"

urlpatterns = [
    path("projects/", ProjectListCreateView.as_view(), name="project-list"),
    path("projects/<int:pk>/", ProjectDetailView.as_view(), name="project-detail"),
    path("projects/<int:pk>/budget/", ProjectBudgetView.as_view(), name="project-budget"),
    path("project-criteria/", ProjectCriteriaListView.as_view(), name="criteria-list"),
]
