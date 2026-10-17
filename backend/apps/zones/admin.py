from django.contrib import admin

from apps.common.admin import SuperAdminOnlyModelAdmin
from .models import Zone, Region, Department


@admin.register(Region)
class RegionAdmin(SuperAdminOnlyModelAdmin, admin.ModelAdmin):
    list_display = ["nom", "created_at"]
    search_fields = ["nom"]


@admin.register(Department)
class DepartmentAdmin(SuperAdminOnlyModelAdmin, admin.ModelAdmin):
    list_display = ["nom", "region", "created_at"]
    search_fields = ["nom"]
    list_filter = ["region"]


@admin.register(Zone)
class ZoneAdmin(SuperAdminOnlyModelAdmin, admin.ModelAdmin):
    list_display = ["nom", "region", "departement", "rayon", "statut", "created_at"]
    list_filter = ["region", "departement", "statut"]
    search_fields = ["nom"]
    readonly_fields = ["location", "latitude", "longitude", "created_at", "updated_at"]
