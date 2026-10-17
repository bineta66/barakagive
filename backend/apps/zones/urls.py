from django.urls import path

from .views import (
    ReverseGeocodeView,
    DepartmentListView,
    ZoneListView,
    ZoneDetailView,
)

app_name = "zones"

urlpatterns = [
    path("zones/reverse-geocode/", ReverseGeocodeView.as_view(), name="reverse-geocode"),
    path("zones/departements/", DepartmentListView.as_view(), name="department-list"),
    path("zones/departments/", DepartmentListView.as_view(), name="department-list-alias"),
    path("zones/", ZoneListView.as_view(), name="zone-list"),
    path("zones/<uuid:id>/", ZoneDetailView.as_view(), name="zone-detail"),
]
