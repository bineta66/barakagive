from django.contrib import admin

from .models import Budget, Don, Depense, Justification


@admin.register(Budget)
class BudgetAdmin(admin.ModelAdmin):
    list_display = ['id', 'projet', 'montant', 'source_financement', 'date', 'statut']
    list_filter = ['statut', 'date']
    search_fields = ['projet__name', 'source_financement']


@admin.register(Don)
class DonAdmin(admin.ModelAdmin):
    list_display = ['reference', 'bailleur', 'projet', 'montant', 'moyen_paiement', 'date']
    list_filter = ['moyen_paiement', 'date']
    search_fields = ['reference', 'bailleur', 'projet__name']


@admin.register(Depense)
class DepenseAdmin(admin.ModelAdmin):
    list_display = ['reference', 'projet', 'categorie', 'montant', 'fournisseur', 'date', 'statut']
    list_filter = ['statut', 'categorie', 'date']
    search_fields = ['reference', 'projet__name', 'fournisseur']


@admin.register(Justification)
class JustificationAdmin(admin.ModelAdmin):
    list_display = ['id', 'depense', 'type_fichier', 'statut', 'created_at']
    list_filter = ['statut', 'type_fichier']