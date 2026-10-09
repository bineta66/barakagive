from django.urls import path

from .views import (
    RegisterOrganizationView,
    OrganizationListView,
    OrganizationDetailView,
    AdminONGRequestsView,
    ApproveONGView,
    RejectONGView,
    ActivationCheckView,
    ActivationConfirmView,
    OrganisationRequestCreateView,
    OrganizationDocumentView,
)

app_name = "organizations"

urlpatterns = [
    path("register/", RegisterOrganizationView.as_view(), name="register"),
    path("", OrganizationListView.as_view(), name="list"),
    path("<int:pk>/", OrganizationDetailView.as_view(), name="detail"),
    path("<int:pk>/documents/<str:document_type>/", OrganizationDocumentView.as_view(), name="document"),
    path("admin/demandes/", AdminONGRequestsView.as_view(), name="admin-demandes"),
    path("admin/<int:pk>/approve/", ApproveONGView.as_view(), name="admin-approve"),
    path("admin/<int:pk>/reject/", RejectONGView.as_view(), name="admin-reject"),
    path("activation/check/<uuid:token>/", ActivationCheckView.as_view(), name="activation-check"),
    path("activation/", ActivationConfirmView.as_view(), name="activation-confirm"),

    # ── Demandes d'inscription ONG (nouveau module) ──────────────────────
    path("request/", OrganisationRequestCreateView.as_view(), name="org-request-create"),
]
