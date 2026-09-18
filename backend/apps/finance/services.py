from decimal import Decimal

from django.db import transaction
from django.db.models import Sum, Count

from .models import Depense, Budget, PosteBudgetaire


@transaction.atomic
def validate_budget_amount(don, amount):
    if amount > don.montant_restant:
        raise ValueError("Le budget dépasse le montant restant du don.")


@transaction.atomic
def create_depense(validated_data, user, has_justificatif=False):
    poste = validated_data["poste_budgetaire"]
    amount = validated_data["montant"]
    status = Depense.Status.EXCEPTION if amount > poste.montant_restant else (
        Depense.Status.A_VERIFIER if has_justificatif else Depense.Status.EN_ATTENTE
    )
    return Depense.objects.create(
        **validated_data,
        organization=user.organization,
        created_by=user,
        statut=status,
    )


def recalculate_poste(poste):
    total = poste.depenses.filter(statut=Depense.Status.APPROUVEE).aggregate(
        total=Sum("montant")
    )["total"] or Decimal("0")
    poste.montant_depense = total
    poste.save(update_fields=["montant_depense", "updated_at"])


def analyse_budgetaire(projet):
    """
    Construit l'analyse budgétaire d'un projet.

    Args:
        projet: Instance de Project

    Returns:
        dict: Analyse budgétaire avec dépenses, taux d'exécution, alertes, etc.
    """
    budgets = Budget.objects.filter(projet=projet, statut__in=[Budget.Status.EN_COURS, Budget.Status.APPROUVE])
    budget_total = budgets.aggregate(total=Sum("montant_total"))["total"] or Decimal("0")

    depenses = Depense.objects.filter(
        projet=projet,
        statut=Depense.Status.APPROUVEE,
    ).select_related("poste_budgetaire")

    depenses_totales = depenses.aggregate(total=Sum("montant"))["total"] or Decimal("0")
    solde = budget_total - depenses_totales

    taux_execution = 0
    if budget_total > 0:
        taux_execution = int((depenses_totales / budget_total) * 100)

    if taux_execution <= 50:
        alerte = "Vert"
    elif taux_execution <= 70:
        alerte = "Jaune"
    elif taux_execution <= 90:
        alerte = "Orange"
    else:
        alerte = "Rouge"

    depenses_par_categorie = {}
    depenses_par_zone = {}
    for depense in depenses:
        libelle = depense.poste_budgetaire.libelle if depense.poste_budgetaire else "Autre"
        zone = getattr(depense, "zone", None)
        zone_nom = zone.nom if hasattr(zone, "nom") else (depense.zone if hasattr(depense, "zone") and depense.zone else "Inconnue")
        depenses_par_categorie[libelle] = depenses_par_categorie.get(libelle, Decimal("0")) + depense.montant
        depenses_par_zone[zone_nom] = depenses_par_zone.get(zone_nom, Decimal("0")) + depense.montant

    categorie_plus_depensiere = max(depenses_par_categorie, key=depenses_par_categorie.get) if depenses_par_categorie else ""
    zone_plus_depensiere = max(depenses_par_zone, key=depenses_par_zone.get) if depenses_par_zone else ""

    return {
        "budget_total": float(budget_total),
        "depenses_totales": float(depenses_totales),
        "solde": float(solde),
        "taux_execution": taux_execution,
        "alerte": alerte,
        "categorie_plus_depensiere": categorie_plus_depensiere,
        "zone_plus_depensiere": zone_plus_depensiere,
    }