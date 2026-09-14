from django.urls import path

from .views import (
    RegisterOrganizationView,
    OrganizationListView,
)

app_name = "organizations"

urlpatterns = [
    path("register/", RegisterOrganizationView.as_view(), name="register"),
    path("", OrganizationListView.as_view(), name="list"),
]