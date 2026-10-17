from django.contrib import admin
from apps.common.admin import SuperAdminOnlyModelAdmin
from .models import Budget, Don, Depense, Justification, LigneBudgetaire, Donateur, Financement, Bailleur, Partenaire


@admin.register(Budget)
class BudgetAdmin(SuperAdminOnlyModelAdmin, admin.ModelAdmin):
    list_display = (
        "projet",
        "montant",
        "devise",
        "source_financement",
        "statut",
        "date",
        "organization",
    )
    list_filter = ("statut", "date", "organization")
    search_fields = ("projet__name", "source_financement")
    ordering = ("-date",)


@admin.register(LigneBudgetaire)
class LigneBudgetaireAdmin(SuperAdminOnlyModelAdmin, admin.ModelAdmin):
    list_display = ("libelle", "budget", "categorie", "montant_prevu", "montant_revise")
    list_filter = ("categorie", "organization")
    search_fields = ("libelle", "categorie")


@admin.register(Donateur)
class DonateurAdmin(SuperAdminOnlyModelAdmin, admin.ModelAdmin):
    list_display = ("nom", "type", "email", "telephone", "actif", "organization")
    list_filter = ("type", "actif", "organization")
    search_fields = ("nom", "email", "telephone")


@admin.register(Financement)
class FinancementAdmin(SuperAdminOnlyModelAdmin, admin.ModelAdmin):
    list_display = ("reference", "projet", "bailleur", "type", "montant", "devise", "statut", "date")
    list_filter = ("type", "statut", "date", "organization")
    search_fields = ("reference", "projet__name", "observation")


@admin.register(Don)
class DonAdmin(SuperAdminOnlyModelAdmin, admin.ModelAdmin):
    list_display = (
        "reference",
        "donateur",
        "campagne",
        "montant",
        "devise",
        "moyen_paiement",
        "date",
    )
    list_filter = ("moyen_paiement", "date", "organization")
    search_fields = (
        "reference",
        "donateur__nom",
        "campagne__nom",
    )
    ordering = ("-date",)


@admin.register(Depense)
class DepenseAdmin(SuperAdminOnlyModelAdmin, admin.ModelAdmin):
    list_display = (
        "reference",
        "projet",
        "campagne",
        "categorie",
        "montant",
        "devise",
        "statut",
        "date",
    )
    list_filter = (
        "statut",
        "categorie",
        "date",
        "organization",
    )
    search_fields = (
        "reference",
        "projet__name",
        "campagne__nom",
        "fournisseur",
    )
    ordering = ("-date",)


@admin.register(Justification)
class JustificationAdmin(SuperAdminOnlyModelAdmin, admin.ModelAdmin):
    list_display = (
        "depense",
        "type_fichier",
        "statut",
        "uploaded_by",
        "valide_par",
        "created_at",
    )
    list_filter = ("statut", "type_fichier")
    search_fields = (
        "depense__reference",
        "uploaded_by__username",
    )
    ordering = ("-created_at",)


@admin.register(Bailleur)
class BailleurAdmin(SuperAdminOnlyModelAdmin, admin.ModelAdmin):
    list_display = ("nom", "type", "email", "telephone", "actif", "organization")
    list_filter = ("actif", "organization")
    search_fields = ("nom", "email")


@admin.register(Partenaire)
class PartenaireAdmin(SuperAdminOnlyModelAdmin, admin.ModelAdmin):
    list_display = ("nom", "domaine", "email", "telephone", "actif", "organization")
    list_filter = ("actif", "organization")
    search_fields = ("nom", "email")
