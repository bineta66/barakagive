import uuid
from datetime import date
from django.conf import settings
from django.db import models
from django.db.models.signals import post_delete, pre_save
from django.dispatch import receiver


class FinanceOwnedModel(models.Model):
    organization = models.ForeignKey(
        "organizations.Organization",
        on_delete=models.CASCADE,
        related_name="%(app_label)s_%(class)s_set",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Budget(FinanceOwnedModel):
    class Status(models.TextChoices):
        BROUILLON = "BROUILLON", "Brouillon"
        EN_COURS = "EN_COURS", "En cours"
        APPROUVE = "APPROUVE", "Approuvé"
        CLOTURE = "CLOTURE", "Clôturé"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    projet = models.ForeignKey("projects.Project", on_delete=models.PROTECT, related_name="budgets")
    montant = models.DecimalField(max_digits=14, decimal_places=2)
    source_financement = models.CharField(max_length=255)
    date = models.DateField(default=date.today)
    observation = models.TextField(blank=True)
    statut = models.CharField(max_length=20, choices=Status.choices, default=Status.BROUILLON)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="created_budgets",
    )

    @property
    def solde(self):
        dons = self.dons.aggregate(total=models.Sum('montant'))['total'] or 0
        depenses = self.depenses.aggregate(total=models.Sum('montant'))['total'] or 0
        return dons - depenses

    @property
    def taux_execution(self):
        if self.montant == 0:
            return 0
        depenses = self.depenses.aggregate(total=models.Sum('montant'))['total'] or 0
        return round((depenses / self.montant) * 100, 2)


class Don(FinanceOwnedModel):
    class MoyenPaiement(models.TextChoices):
        VIREMENT = "VIREMENT", "Virement"
        ESPECE = "ESPECE", "Espèce"
        CHEQUE = "CHEQUE", "Chèque"
        CARTE = "CARTE", "Carte"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    reference = models.CharField(max_length=40, unique=True, blank=True)
    bailleur = models.CharField(max_length=255)
    projet = models.ForeignKey("projects.Project", on_delete=models.PROTECT, related_name="dons")
    campagne = models.ForeignKey("campaigns.Campaign", on_delete=models.SET_NULL, null=True, blank=True, related_name="dons")
    budget = models.ForeignKey(Budget, on_delete=models.PROTECT, related_name="dons")
    montant = models.DecimalField(max_digits=14, decimal_places=2)
    moyen_paiement = models.CharField(max_length=20, choices=MoyenPaiement.choices, default=MoyenPaiement.VIREMENT)
    date = models.DateField(default=date.today)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="created_dons",
    )


class Depense(FinanceOwnedModel):
    class Status(models.TextChoices):
        EN_ATTENTE = "EN_ATTENTE", "En attente"
        VERIFIE = "VERIFIE", "Vérifié"
        APPROUVE = "APPROUVE", "Approuvé"
        REJETE = "REJETE", "Rejeté"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    reference = models.CharField(max_length=40, unique=True, blank=True)
    projet = models.ForeignKey("projects.Project", on_delete=models.PROTECT, related_name="depenses")
    campagne = models.ForeignKey("campaigns.Campaign", on_delete=models.SET_NULL, null=True, blank=True, related_name="depenses")
    region = models.CharField(max_length=255, blank=True)
    categorie = models.CharField(max_length=100)
    montant = models.DecimalField(max_digits=14, decimal_places=2)
    fournisseur = models.CharField(max_length=255, blank=True)
    date = models.DateField(default=date.today)
    description = models.TextField(blank=True)
    statut = models.CharField(max_length=20, choices=Status.choices, default=Status.EN_ATTENTE)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="created_depenses",
    )


class Justification(models.Model):
    class Status(models.TextChoices):
        CONFORME = "CONFORME", "Conforme"
        A_VERIFIER = "A_VERIFIER", "À vérifier"
        NON_CONFORME = "NON_CONFORME", "Non conforme"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    depense = models.ForeignKey(Depense, on_delete=models.CASCADE, related_name="justifications")
    fichier = models.FileField(upload_to="justifications/")
    type_fichier = models.CharField(max_length=20)
    statut = models.CharField(max_length=20, choices=Status.choices, default=Status.A_VERIFIER)
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


@receiver(pre_save, sender=Don)
def generate_don_reference(sender, instance, **kwargs):
    if not instance.reference:
        if isinstance(instance.date, date):
            year = instance.date.year
        else:
            from datetime import datetime
            year = datetime.strptime(str(instance.date), '%Y-%m-%d').date().year
        instance.reference = f"DON-{year}-{uuid.uuid4().hex[:8].upper()}"


@receiver(pre_save, sender=Depense)
def generate_depense_reference(sender, instance, **kwargs):
    if not instance.reference:
        if isinstance(instance.date, date):
            year = instance.date.year
        else:
            from datetime import datetime
            year = datetime.strptime(str(instance.date), '%Y-%m-%d').date().year
        instance.reference = f"DEP-{year}-{uuid.uuid4().hex[:8].upper()}"


@receiver(post_delete, sender=Justification)
def delete_justification_file(sender, instance, **kwargs):
    if instance.fichier:
        instance.fichier.delete(save=False)