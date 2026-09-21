from django.db.models import Sum
from .models import Budget, Don, Depense


def prepare_budget_analysis(campaign_id):
    """
    Prépare les données financières pour l'analyse IA.
    Ces données sont envoyées à FastAPI pour générer l'analyse.
    """
    # Obtenir les budgets liés à la campagne
    budgets = Budget.objects.filter(campaign_id=campaign_id)
    
    budget_total = budgets.aggregate(total=Sum('montant'))['total'] or 0
    dons_total = Don.objects.filter(budget__in=budgets).aggregate(total=Sum('montant'))['total'] or 0
    depenses_total = Depense.objects.filter(budget__in=budgets).aggregate(total=Sum('montant'))['total'] or 0
    solde = dons_total - depenses_total
    
    taux_execution = 0
    if budget_total > 0:
        taux_execution = round((depenses_total / budget_total) * 100, 2)
    
    # Dépenses par catégorie
    depenses_par_categorie = Depense.objects.filter(
        budget__in=budgets
    ).values('categorie').annotate(
        total=Sum('montant')
    ).order_by('-total')
    
    # Dépenses par région
    depenses_par_region = Depense.objects.filter(
        budget__in=budgets
    ).values('region').annotate(
        total=Sum('montant')
    ).order_by('-total')
    
    return {
        "budget_total": float(budget_total),
        "dons_reçus": float(dons_total),
        "depenses_totales": float(depenses_total),
        "solde": float(solde),
        "taux_execution": taux_execution,
        "depenses_par_categorie": list(depenses_par_categorie),
        "depenses_par_region": list(depenses_par_region),
    }