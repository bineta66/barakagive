from decimal import Decimal
from datetime import date

from django.db import transaction
from django.db.models import Q, Sum, F, Count
from django.db.models.functions import TruncMonth
from django.utils import timezone
from rest_framework.exceptions import ValidationError

from apps.campaigns.models import Campaign
from .models import Budget, Don, Depense, Financement, LigneBudgetaire
from apps.projects.models import Project


RESERVING_EXPENSE_STATUSES = (
    Depense.Status.EN_ATTENTE,
    Depense.Status.VERIFIE,
    Depense.Status.APPROUVE,
)


def _money(value):
    return Decimal(value or 0)


def _organization_donations(organization):
    return Don.objects.filter(organization=organization).filter(
        Q(campagne__isnull=True) | Q(campagne__organization=organization, campagne__projet__organization=organization),
        Q(donateur__isnull=True) | Q(donateur__organization=organization),
    )


def _organization_financings(organization):
    return Financement.objects.filter(organization=organization, projet__organization=organization).filter(
        Q(budget__isnull=True) | Q(budget__organization=organization, budget__projet__organization=organization),
        Q(campagne__isnull=True) | Q(campagne__organization=organization, campagne__projet__organization=organization),
        Q(bailleur__isnull=True) | Q(bailleur__organization=organization),
    )


def _organization_expenses(organization):
    return Depense.objects.filter(organization=organization).filter(
        Q(projet__isnull=True) | Q(projet__organization=organization),
        Q(budget__isnull=True) | Q(budget__organization=organization, budget__projet__organization=organization),
        Q(ligne_budgetaire__isnull=True) | Q(ligne_budgetaire__organization=organization, ligne_budgetaire__budget__organization=organization, ligne_budgetaire__budget__projet__organization=organization),
        Q(campagne__isnull=True) | Q(campagne__organization=organization, campagne__projet__organization=organization),
    )


def _committed_expenses(project, budget=None, line=None, exclude_expense=None):
    expenses = _organization_expenses(project.organization).filter(statut__in=RESERVING_EXPENSE_STATUSES).filter(
        Q(projet=project) | Q(budget__projet=project) | Q(ligne_budgetaire__budget__projet=project) | Q(campagne__projet=project)
    )
    if budget is not None:
        expenses = expenses.filter(Q(budget=budget) | Q(ligne_budgetaire__budget=budget))
    if line is not None:
        expenses = expenses.filter(ligne_budgetaire=line)
    if exclude_expense is not None:
        expenses = expenses.exclude(pk=exclude_expense)
    return _money(expenses.aggregate(total=Sum("montant"))["total"])


def _received_for_project(project, exclude_financement=None, exclude_don=None):
    financings = _organization_financings(project.organization).filter(projet=project, statut=Financement.Status.RECU)
    donations = _organization_donations(project.organization).filter(campagne__projet=project)
    if exclude_financement is not None:
        financings = financings.exclude(pk=exclude_financement)
    if exclude_don is not None:
        donations = donations.exclude(pk=exclude_don)
    return _money(financings.aggregate(total=Sum("montant"))["total"]) + _money(donations.aggregate(total=Sum("montant"))["total"])


def calculate_financial_kpis(organization, project=None):
    if organization is None:
        return {"budget_total": 0.0, "financement_total": 0.0, "financements_recus": 0.0, "dons_recus": 0.0, "depenses_totales": 0.0, "depenses_engagees": 0.0, "depenses_validees": 0.0, "solde": 0.0, "solde_tresorerie": None, "taux_financement": 0.0, "taux_engagement": 0.0, "taux_execution": 0.0}
    budgets = Budget.objects.filter(organization=organization, projet__organization=organization)
    financings = _organization_financings(organization).filter(statut=Financement.Status.RECU)
    donations = _organization_donations(organization)
    expenses = _organization_expenses(organization).filter(statut=Depense.Status.APPROUVE)
    committed = _organization_expenses(organization).filter(statut__in=RESERVING_EXPENSE_STATUSES)
    if project is not None:
        budgets = budgets.filter(projet=project)
        financings = financings.filter(projet=project)
        donations = donations.filter(campagne__projet=project)
        project_scope = Q(projet=project) | Q(budget__projet=project) | Q(ligne_budgetaire__budget__projet=project) | Q(campagne__projet=project)
        expenses = expenses.filter(project_scope)
        committed = committed.filter(project_scope)
    budget_total = _money(budgets.aggregate(total=Sum("montant"))["total"])
    funding_total = _money(financings.aggregate(total=Sum("montant"))["total"])
    donations_total = _money(donations.aggregate(total=Sum("montant"))["total"])
    approved_total = _money(expenses.aggregate(total=Sum("montant"))["total"])
    committed_total = _money(committed.aggregate(total=Sum("montant"))["total"])
    return {
        "budget_total": float(budget_total), "financement_total": float(funding_total),
        "financements_recus": float(funding_total), "dons_recus": float(donations_total),
        "depenses_totales": float(approved_total), "depenses_engagees": float(committed_total),
        "depenses_validees": float(approved_total), "solde": float(budget_total - committed_total),
        "solde_tresorerie": None,
        "taux_financement": round(float((funding_total + donations_total) / budget_total * 100), 2) if budget_total else 0.0,
        "taux_engagement": round(float(committed_total / budget_total * 100), 2) if budget_total else 0.0,
        "taux_execution": round(float(approved_total / budget_total * 100), 2) if budget_total else 0.0,
    }


def build_finance_dashboard(organization):
    kpis = calculate_financial_kpis(organization)
    budgets = Budget.objects.filter(organization=organization, projet__organization=organization).select_related("projet").order_by("projet__name", "created_at")
    budget_rows = []
    for budget in budgets:
        expenses = _organization_expenses(organization).filter(Q(budget=budget) | Q(ligne_budgetaire__budget=budget))
        approved = _money(expenses.filter(statut=Depense.Status.APPROUVE).aggregate(total=Sum("montant"))["total"])
        committed = _money(expenses.filter(statut__in=RESERVING_EXPENSE_STATUSES).aggregate(total=Sum("montant"))["total"])
        amount = _money(budget.montant)
        budget_rows.append({"id": str(budget.pk), "projet": budget.projet.name, "budget_prevu": float(amount), "budget_revise": None, "depenses_engagees": float(committed), "depenses_validees": float(approved), "disponible": float(amount - committed), "taux_execution": round(float(approved / amount * 100), 2) if amount else 0, "taux_engagement": round(float(committed / amount * 100), 2) if amount else 0, "financements_recus": float(_money(_organization_financings(organization).filter(budget=budget, statut=Financement.Status.RECU).aggregate(total=Sum("montant"))["total"])), "statut": budget.statut})
    funding_by_status = {code: float(_money(_organization_financings(organization).filter(statut=code).aggregate(total=Sum("montant"))["total"])) for code, _ in Financement.Status.choices}
    expense_counts = {row["statut"]: row["count"] for row in _organization_expenses(organization).values("statut").annotate(count=Count("id"))}
    category_rows = _organization_expenses(organization).filter(statut=Depense.Status.APPROUVE).values("categorie").annotate(montant=Sum("montant")).order_by("-montant")
    last_donation = _organization_donations(organization).order_by("-date", "-created_at").first()
    months = []
    today = timezone.localdate()
    for offset in range(12):
        idx = today.year * 12 + today.month - 1 - 11 + offset
        year, month = divmod(idx, 12)
        months.append({"key": f"{year}-{month + 1:02d}", "label": date(year, month + 1, 1).strftime("%b %Y"), "financements_recus": 0.0, "dons_recus": 0.0, "depenses_validees": 0.0})
    start_date = date.fromisoformat(months[0]["key"] + "-01")
    month_index = {row["key"]: row for row in months}
    for model, query, key in ((Financement, _organization_financings(organization).filter(statut=Financement.Status.RECU), "financements_recus"), (Don, _organization_donations(organization), "dons_recus"), (Depense, _organization_expenses(organization).filter(statut=Depense.Status.APPROUVE), "depenses_validees")):
        for row in query.filter(date__gte=start_date).annotate(month=TruncMonth("date")).values("month").annotate(total=Sum("montant")):
            if row["month"]:
                point = month_index.get(row["month"].strftime("%Y-%m"))
                if point: point[key] = float(_money(row["total"]))
    funding_pending = _money(_organization_financings(organization).filter(statut__in=[Financement.Status.PREVU, Financement.Status.CONFIRME]).aggregate(total=Sum("montant"))["total"])
    return {**kpis, "kpis": {"budget_total": kpis["budget_total"], "financements_recus": kpis["financements_recus"], "dons_recus": kpis["dons_recus"], "depenses_validees": kpis["depenses_validees"], "solde_disponible": kpis["solde"]}, "reste_a_financer": max(0, kpis["budget_total"] - kpis["financements_recus"] - kpis["dons_recus"]), "reste_a_depenser": kpis["solde"], "execution_budgetaire": {"budget_prevu": kpis["budget_total"], "budget_revise": None, "depenses_engagees": kpis["depenses_engagees"], "depenses_validees": kpis["depenses_validees"], "disponible": kpis["solde"], "taux_execution": kpis["taux_execution"], "par_budget": budget_rows}, "financements": {"par_statut": funding_by_status, "reste_a_financer": max(0, kpis["budget_total"] - kpis["financements_recus"] - kpis["dons_recus"]), "par_bailleur": list(_organization_financings(organization).filter(statut=Financement.Status.RECU, bailleur__isnull=False).values("bailleur__nom").annotate(montant=Sum("montant")).order_by("-montant"))}, "dons": {"nombre_donateurs": _organization_donations(organization).filter(donateur__isnull=False).values("donateur_id").distinct().count(), "dernier_don": ({"montant": float(last_donation.montant), "date": last_donation.date.isoformat(), "reference": last_donation.reference} if last_donation else None)}, "depenses": {"par_statut": expense_counts, "par_categorie": [{"categorie": x["categorie"], "montant": float(_money(x["montant"]))} for x in category_rows]}, "evolution": months, "alerts": [], "ai_analysis": None}


def _format_fcfa(value):
    return f"{_money(value):,.0f}".replace(",", " ")


def _effective_project(serializer, attrs):
    instance = serializer.instance
    project = attrs.get("projet", getattr(instance, "projet", None) if instance else None)
    budget = attrs.get("budget", getattr(instance, "budget", None) if instance else None)
    line = attrs.get("ligne_budgetaire", getattr(instance, "ligne_budgetaire", None) if instance else None)
    campaign = attrs.get("campagne", getattr(instance, "campagne", None) if instance else None)
    return project or (budget.projet if budget else None) or (line.budget.projet if line else None) or (campaign.projet if campaign else None)


def save_financially_locked(serializer, user):
    attrs, instance = serializer.validated_data, serializer.instance
    project = _effective_project(serializer, attrs)
    if project is None:
        return serializer.save(organization=user.organization, created_by=user) if instance is None else serializer.save()
    with transaction.atomic():
        locked_project = Project.objects.select_for_update().get(pk=project.pk, organization_id=user.organization_id)
        locked_budgets = list(Budget.objects.select_for_update().filter(organization_id=user.organization_id, projet=locked_project).order_by("pk"))
        if instance is not None:
            instance = instance.__class__.objects.select_for_update().get(pk=instance.pk)
            serializer.instance = instance
        model = serializer.Meta.model
        if model is Budget:
            new_amount = _money(attrs.get("montant", instance.montant if instance else 0))
            old_amount = _money(instance.montant) if instance else Decimal("0")
            total = sum((_money(b.montant) for b in locked_budgets), Decimal("0")) - old_amount + new_amount
            received = _received_for_project(locked_project)
            committed = _committed_expenses(locked_project)
            if total < received: raise ValidationError({"montant": "Le budget ne peut pas être inférieur aux financements reçus."})
            if total < committed: raise ValidationError({"montant": "Le budget ne peut pas être inférieur aux dépenses engagées."})
        elif model is Financement:
            amount = _money(attrs.get("montant", instance.montant if instance else 0))
            status = attrs.get("statut", instance.statut if instance else Financement.Status.CONFIRME)
            if status == Financement.Status.RECU:
                capacity = sum((_money(b.montant) for b in locked_budgets), Decimal("0"))
                if _received_for_project(locked_project, exclude_financement=instance.pk if instance else None) + amount > capacity:
                    raise ValidationError({"montant": "Le financement reçu dépasse le budget autorisé du projet."})
        elif model is Don:
            campaign = attrs.get("campagne", instance.campagne if instance else None)
            if campaign:
                amount = _money(attrs.get("montant", instance.montant if instance else 0))
                capacity = sum((_money(b.montant) for b in locked_budgets), Decimal("0"))
                if _received_for_project(locked_project, exclude_don=instance.pk if instance else None) + amount > capacity:
                    raise ValidationError({"montant": "Le don dépasse le montant restant du budget autorisé."})
        elif model is Depense:
            amount = _money(attrs.get("montant", instance.montant if instance else 0))
            status = attrs.get("statut", instance.statut if instance else Depense.Status.EN_ATTENTE)
            budget = attrs.get("budget", instance.budget if instance else None)
            line = attrs.get("ligne_budgetaire", instance.ligne_budgetaire if instance else None)
            exclude = instance.pk if instance else None
            if status in RESERVING_EXPENSE_STATUSES:
                project_cap = sum((_money(b.montant) for b in locked_budgets), Decimal("0"))
                project_used = _committed_expenses(locked_project, exclude_expense=exclude)
                if project_used + amount > project_cap: raise ValidationError({"montant": "La dépense dépasse le budget disponible du projet."})
                effective_budget = budget or (line.budget if line else None)
                if effective_budget and _committed_expenses(locked_project, budget=effective_budget, exclude_expense=exclude) + amount > _money(effective_budget.montant):
                    raise ValidationError({"montant": "La dépense dépasse le budget disponible."})
                if line:
                    cap = _money(line.montant_revise if line.montant_revise is not None else line.montant_prevu)
                    if _committed_expenses(locked_project, line=line, exclude_expense=exclude) + amount > cap:
                        raise ValidationError({"montant": "La dépense dépasse le plafond de la ligne budgétaire."})
        elif model is LigneBudgetaire:
            budget = attrs.get("budget", instance.budget if instance else None)
            if budget:
                planned = _money(attrs.get("montant_prevu", instance.montant_prevu if instance else 0))
                revised = attrs.get("montant_revise", instance.montant_revise if instance else None)
                cap = _money(revised if revised is not None else planned)
                used = _committed_expenses(locked_project, line=instance) if instance else Decimal("0")
                if used > cap: raise ValidationError({"montant_prevu": "Le plafond ne peut pas être inférieur aux dépenses engagées."})
                other_lines = LigneBudgetaire.objects.filter(budget=budget).exclude(pk=instance.pk if instance else None)
                line_total = sum((_money(item.montant_revise if item.montant_revise is not None else item.montant_prevu) for item in other_lines), Decimal("0"))
                if line_total + cap > _money(budget.montant): raise ValidationError({"montant_prevu": "Le total des lignes ne peut pas dépasser le budget."})
        kwargs = {"organization": user.organization}
        if instance is None: kwargs["created_by"] = user
        return serializer.save(**kwargs)


def delete_financially_locked(instance, user):
    project = getattr(instance, "projet", None)
    if project is None and getattr(instance, "budget_id", None): project = instance.budget.projet
    if project is None and getattr(instance, "ligne_budgetaire_id", None): project = instance.ligne_budgetaire.budget.projet
    if project is None and getattr(instance, "campagne_id", None): project = instance.campagne.projet
    if project is None:
        instance.delete()
        return
    with transaction.atomic():
        Project.objects.select_for_update().get(pk=project.pk, organization_id=user.organization_id)
        locked = instance.__class__.objects.select_for_update().get(pk=instance.pk)
        if isinstance(locked, Budget) and (locked.financements.exists() or locked.depenses.exists() or locked.lignes_budgetaires.exists()):
            raise ValidationError({"detail": "Ce budget est utilisé par des opérations et ne peut pas être supprimé."})
        if isinstance(locked, LigneBudgetaire) and locked.depenses.exists():
            raise ValidationError({"detail": "Cette ligne est utilisée par des dépenses et ne peut pas être supprimée."})
        locked.delete()


def prepare_budget_analysis(campaign_id):
    campaign = Campaign.objects.select_related("projet").get(id=campaign_id, projet__organization_id=F("organization_id"))
    project = campaign.projet
    kpis = calculate_financial_kpis(campaign.organization, project=project)
    expenses = _organization_expenses(campaign.organization).filter(statut=Depense.Status.APPROUVE).filter(Q(projet=project) | Q(budget__projet=project) | Q(campagne__projet=project))
    by_category = expenses.values("categorie").annotate(montant=Sum("montant")).order_by("-montant")
    return {"campagne": {"id": str(campaign.id), "nom": campaign.nom, "date_fin": campaign.date_fin, "jours_restants": max(0, (campaign.date_fin - campaign.date_debut).days)}, "budget_total": kpis["budget_total"], "dons_recus": kpis["dons_recus"], "depenses_totales": kpis["depenses_validees"], "financements_recus": kpis["financements_recus"], "solde": kpis["solde"], "taux_financement": kpis["taux_financement"], "taux_execution": kpis["taux_execution"], "depenses_par_categorie": list(by_category), "depenses_par_region": []}
