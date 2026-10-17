from django.contrib import admin

from apps.common.admin import SuperAdminOnlyModelAdmin
from .models import Project, ProjectCriteria


@admin.register(Project)
class ProjectAdmin(SuperAdminOnlyModelAdmin, admin.ModelAdmin):
    list_display = ["name", "code", "region", "archived", "created_at"]
    list_filter = ["archived", "region"]
    search_fields = ["name", "code"]
    readonly_fields = ["code", "created_at", "updated_at"]


@admin.register(ProjectCriteria)
class ProjectCriteriaAdmin(SuperAdminOnlyModelAdmin, admin.ModelAdmin):
    list_display = ["projet", "nom", "poids", "actif", "created_by", "created_at"]
    list_filter = ["actif", "projet"]
    search_fields = ["nom", "projet__name"]
    readonly_fields = ["created_by", "created_at"]
