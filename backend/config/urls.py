from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import JsonResponse
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
)
from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from apps.accounts.permissions import IsAccountActive, IsSuperAdmin

def health_check(request):
    return JsonResponse({"status": "ok", "service": "barakagive-backend"})

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/superadmin/dashboard/", __import__("apps.organizations.dashboard", fromlist=["SuperAdminDashboardView"]).SuperAdminDashboardView.as_view(), name="superadmin-dashboard"),

    path("api/accounts/", include("apps.accounts.urls")),
    path("api/auth/", include(("apps.accounts.urls", "auth"), namespace="auth")),
    path("api/token/", __import__("apps.accounts.jwt_views", fromlist=["JWTLoginView"]).JWTLoginView.as_view(), name="token_obtain_pair"),
    path("api/token/refresh/", __import__("apps.accounts.jwt_views", fromlist=["ActiveTokenRefreshView"]).ActiveTokenRefreshView.as_view(), name="token_refresh"),
    path("api/organizations/", include("apps.organizations.urls")),
    path("api/agent/", include("apps.campaigns.agent_urls")),
    path("api/campaigns/", include("apps.campaigns.urls")),
    path("api/", include("apps.projects.urls")),
    path("api/", include("apps.zones.urls")),
    path("api/regions/", __import__("apps.zones.views", fromlist=["RegionListView"]).RegionListView.as_view(), name="region-list"),
    path("api/forms/", include("apps.forms.urls")),
    path("api/beneficiaries/", include("apps.beneficiaries.urls")),
    path("api/finance/", include("apps.finance.urls")),
    path("api/ia/", include("apps.ia.urls")),
    path("api/ia/rapport/generate", __import__(
        "apps.finance.views", fromlist=["FinanceReportGenerationView"]
    ).FinanceReportGenerationView.as_view(), name="ia-finance-report-generate"),
    path("api/assistant/dashboard/", __import__("apps.ia.views", fromlist=["AssistantDashboardView"]).AssistantDashboardView.as_view(), name="assistant-dashboard"),
    path("api/assistant/chat/", __import__("apps.ia.views", fromlist=["AssistantChatView"]).AssistantChatView.as_view(), name="assistant-chat"),
    path("api/assistant/audio/", __import__("apps.ia.views", fromlist=["AssistantAudioTranscriptionView"]).AssistantAudioTranscriptionView.as_view(), name="assistant-audio"),
    path("api/payment/", include("apps.payment.urls")),
    path("api/reports/", include("apps.reports.urls")),
    # Carte des Priorités — endpoints régions
    path("api/projets/<int:project_id>/regions/",
         __import__("apps.beneficiaries.views", fromlist=["ProjectRegionsView"]).ProjectRegionsView.as_view(),
         name="project-regions"),
    path("api/projets/<int:project_id>/regions/<str:region_name>/priorites/",
         __import__("apps.beneficiaries.views", fromlist=["RegionPrioritiesView"]).RegionPrioritiesView.as_view(),
         name="region-priorities"),
    path("api/zones/<uuid:zone_id>/beneficiaires/",
         __import__("apps.beneficiaries.views", fromlist=["ZoneBeneficiariesTableView"]).ZoneBeneficiariesTableView.as_view(),
         name="zone-beneficiaires-table"),

    # Health check endpoint for PWA connectivity
    path("api/health/", health_check, name="health-check"),

    # ── Super Admin — Vérification des demandes ONG ──────────────────────
    path("api/superadmin/organisations/",
         __import__("apps.organizations.views", fromlist=["OrganisationRequestListView"]).OrganisationRequestListView.as_view(),
         name="superadmin-org-list"),
    path("api/superadmin/organisations/<str:pk>/",
         __import__("apps.organizations.views", fromlist=["OrganisationRequestDetailView"]).OrganisationRequestDetailView.as_view(),
         name="superadmin-org-detail"),
    path("api/superadmin/organisations/<uuid:pk>/documents/<str:document_type>/",
         __import__("apps.organizations.views", fromlist=["OrganisationRequestDocumentView"]).OrganisationRequestDocumentView.as_view(),
         name="superadmin-organisation-document"),
    path("media/organisation_requests/<path:path>",
         __import__("apps.organizations.views", fromlist=["PrivateMediaDenyView"]).PrivateMediaDenyView.as_view()),
    path("media/organizations/documents/<path:path>",
         __import__("apps.organizations.views", fromlist=["PrivateMediaDenyView"]).PrivateMediaDenyView.as_view()),
    path("media/justifications/<path:path>",
         __import__("apps.organizations.views", fromlist=["PrivateMediaDenyView"]).PrivateMediaDenyView.as_view()),
    path("media/reports/<path:path>",
         __import__("apps.organizations.views", fromlist=["PrivateMediaDenyView"]).PrivateMediaDenyView.as_view()),
    path("api/superadmin/organisations/<str:pk>/decision/",
         __import__("apps.organizations.views", fromlist=["OrganisationRequestDecisionView"]).OrganisationRequestDecisionView.as_view(),
         name="superadmin-org-decision"),

    # API Documentation
    path("api/schema/", SpectacularAPIView.as_view(
        authentication_classes=[SessionAuthentication, JWTAuthentication],
        permission_classes=[IsAuthenticated, IsAccountActive, IsSuperAdmin],
    ), name="schema"),
    path("api/swagger/", SpectacularSwaggerView.as_view(
        url_name="schema",
        authentication_classes=[SessionAuthentication, JWTAuthentication],
        permission_classes=[IsAuthenticated, IsAccountActive, IsSuperAdmin],
    ), name="swagger"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
