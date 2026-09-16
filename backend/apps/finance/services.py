from decimal import Decimal

from django.db import transaction

from .models import Depense


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
    from django.db.models import Sum

    total = poste.depenses.filter(statut=Depense.Status.APPROUVEE).aggregate(
        total=Sum("montant")
    )["total"] or Decimal("0")
    poste.montant_depense = total
    poste.save(update_fields=["montant_depense", "updated_at"])