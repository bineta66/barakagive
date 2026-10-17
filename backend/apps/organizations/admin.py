from django.contrib import admin

from apps.common.admin import SuperAdminOnlyModelAdmin
from .models import Organization, OrganisationRequest, AIVerificationReport


@admin.register(Organization)
class OrganizationAdmin(SuperAdminOnlyModelAdmin, admin.ModelAdmin):

    list_display = (
        "name",
        "region",
        "email",
        "status",
        "created_at",
    )

    list_filter = (
        "status",
        "region",
    )

    search_fields = (
        "name",
        "email",
    )


class AIReportInline(admin.StackedInline):
    model = AIVerificationReport
    extra = 0
    readonly_fields = (
        "score_confiance",
        "statut_ia",
        "nom_extrait",
        "ninea_extrait",
        "recepisse_extrait",
        "documents",
        "observation",
        "recommandation",
        "anomalies",
        "created_at",
    )


@admin.register(OrganisationRequest)
class OrganisationRequestAdmin(SuperAdminOnlyModelAdmin, admin.ModelAdmin):
    list_display = (
        "nom_ong",
        "sigle",
        "gerant_nom",
        "gerant_prenom",
        "region",
        "statut",
        "get_score_ia",
        "created_at",
    )
    list_filter = ("statut", "region")
    search_fields = ("nom_ong", "sigle", "gerant_nom", "gerant_email")
    readonly_fields = ("id", "ai_report", "created_at", "updated_at")
    inlines = [AIReportInline]

    @admin.display(description="Score IA")
    def get_score_ia(self, obj):
        report = obj.ai_report
        if isinstance(report, dict):
            return f"{report.get('score_confiance', '-')}%"
        return "-"


@admin.register(AIVerificationReport)
class AIVerificationReportAdmin(SuperAdminOnlyModelAdmin, admin.ModelAdmin):
    list_display = ("request", "score_confiance", "statut_ia", "created_at")
    list_filter = ("statut_ia",)
    readonly_fields = ("id", "request", "raw_response", "created_at")
