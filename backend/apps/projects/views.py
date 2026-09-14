from rest_framework import generics, status
from rest_framework.response import Response

from drf_spectacular.utils import extend_schema

from .models import Project, ProjectCriteria
from .serializers import (
    ProjectSerializer,
    ProjectCreateSerializer,
    BudgetUpdateSerializer,
    ProjectCriteriaSerializer,
)
from .permissions import (
    IsGerantOrFinanceOrAgent,
    CanManageProject,
)


@extend_schema(tags=["Projets"])
class ProjectListCreateView(generics.ListCreateAPIView):
    serializer_class = ProjectSerializer
    permission_classes = [IsGerantOrFinanceOrAgent, CanManageProject]

    def get_queryset(self):
        return Project.objects.select_related(
            "chef_projet", "responsable_finance", "organization", "created_by"
        ).prefetch_related("criteria").all()

    def get_serializer_class(self):
        if self.request.method == "POST":
            return ProjectCreateSerializer
        return ProjectSerializer

    def perform_create(self, serializer):
        serializer.save()


@extend_schema(tags=["Projets"])
class ProjectDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ProjectSerializer
    permission_classes = [IsGerantOrFinanceOrAgent, CanManageProject]
    queryset = Project.objects.select_related(
        "chef_projet", "responsable_finance", "organization", "created_by"
    ).prefetch_related("criteria").all()

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.archived = True
        instance.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


@extend_schema(tags=["Projets"])
class ProjectBudgetView(generics.UpdateAPIView):
    serializer_class = BudgetUpdateSerializer
    permission_classes = [IsGerantOrFinanceOrAgent, CanManageProject]
    queryset = Project.objects.all()

    def get_object(self):
        obj = super().get_object()
        if self.request.user.role not in ["GERANT", "FINANCE"]:
            self.permission_denied(self.request)
        return obj

    def update(self, request, *args, **kwargs):
        project = self.get_object()
        serializer = self.get_serializer(project, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(ProjectSerializer(project).data)


@extend_schema(tags=["Critères Projet"])
class ProjectCriteriaListView(generics.ListCreateAPIView):
    serializer_class = ProjectCriteriaSerializer
    permission_classes = [IsGerantOrFinanceOrAgent]
    queryset = ProjectCriteria.objects.select_related("created_by").all()

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
