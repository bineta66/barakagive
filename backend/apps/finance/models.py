import uuid
from datetime import date

from django.conf import settings
from django.db import models
from django.db.models import Sum
from django.db.models.signals import pre_save, post_save, post_delete
from django.dispatch import receiver


# ==========================
# Modèle abstrait
# ==========================

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


# ==========================
# Budget
# ==========================

class Budget(FinanceOwnedModel):

    class Status(models.TextChoices):
        BROUILLON = "BROUILLON", "Brouillon"
        EN_COURS = "EN_COURS", "En cours"
        APPROUVE = "APPROUVE", "Approuvé"
        CLOTURE = "CLOTURE", "Clôturé"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    projet = models.ForeignKey(
        "projects.Project",
        on_delete=models.PROTECT,
        related_name="budgets",
    )

    montant = models.DecimalField(max_digits=15, decimal_places=2)
    devise = models.CharField(max_length=10, default="XOF")

    source_financement = models.CharField(max_length=255)

    date = models.DateField(default=date.today)

    observation = models.TextField(blank=True)

    statut = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.BROUILLON,
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="created_budgets",
    )

    @property
    def total_depenses(self):
        return self.depenses.filter(
            statut=Depense.Status.APPROUVE,
        ).aggregate(total=Sum("montant"))["total"] or 0

    @property
    def total_depenses_engagees(self):
        return self.depenses.filter(
            statut__in=(
                Depense.Status.EN_ATTENTE,
                Depense.Status.VERIFIE,
                Depense.Status.APPROUVE,
            ),
        ).aggregate(total=Sum("montant"))["total"] or 0

    @property
    def total_financements_recus(self):
        return self.financements.filter(
            statut=Financement.Status.RECU,
        ).aggregate(total=Sum("montant"))["total"] or 0

    @property
    def solde(self):
        """Budget authority remaining after pending, verified and approved expenses."""
        return self.montant - self.total_depenses_engagees

    @property
    def taux_execution(self):
        if self.montant == 0:
            return 0
        return round((self.total_depenses / self.montant) * 100, 2)

    def __str__(self):
        return f"{self.projet.name}"


# ==========================
# Ligne Budgétaire
# ==========================

class LigneBudgetaire(FinanceOwnedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    budget = models.ForeignKey(
        Budget,
        on_delete=models.CASCADE,
        related_name="lignes_budgetaires",
    )
    libelle = models.CharField(max_length=255)
    categorie = models.CharField(max_length=100, blank=True)
    montant_prevu = models.DecimalField(max_digits=15, decimal_places=2)
    montant_revise = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    observation = models.TextField(blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="created_lignes_budgetaires",
    )

    def __str__(self):
        return f"{self.libelle} ({self.budget})"


# ==========================
# Donateur
# ==========================

class Donateur(FinanceOwnedModel):

    class TypeDonateur(models.TextChoices):
        INDIVIDUEL = "INDIVIDUEL", "Individuel"
        ENTREPRISE = "ENTREPRISE", "Entreprise / Organisme"
        ASSOCIATION = "ASSOCIATION", "Association"
        ANONYME = "ANONYME", "Anonyme"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nom = models.CharField(max_length=255)
    email = models.EmailField(blank=True)
    telephone = models.CharField(max_length=50, blank=True)
    type = models.CharField(
        max_length=50,
        choices=TypeDonateur.choices,
        default=TypeDonateur.INDIVIDUEL,
    )
    actif = models.BooleanField(default=True)

    def __str__(self):
        return self.nom


# ==========================
# Don
# ==========================

class Don(FinanceOwnedModel):

    class MoyenPaiement(models.TextChoices):
        VIREMENT = "VIREMENT", "Virement"
        ESPECE = "ESPECE", "Espèce"
        CHEQUE = "CHEQUE", "Chèque"
        CARTE = "CARTE", "Carte"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    reference = models.CharField(max_length=40, unique=True, blank=True)

    donateur = models.ForeignKey(
        Donateur,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="dons",
    )

    campagne = models.ForeignKey(
        "campaigns.Campaign",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="dons",
    )

    montant = models.DecimalField(max_digits=15, decimal_places=2)
    devise = models.CharField(max_length=10, default="XOF")

    moyen_paiement = models.CharField(
        max_length=20,
        choices=MoyenPaiement.choices,
        default=MoyenPaiement.VIREMENT,
    )

    date = models.DateField(default=date.today)

    observation = models.TextField(blank=True)

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="created_dons",
    )

    def __str__(self):
        return self.reference


# ==========================
# Financement
# ==========================

class Financement(FinanceOwnedModel):

    class TypeFinancement(models.TextChoices):
        BAILLEUR = "BAILLEUR", "Bailleur"
        PARTENAIRE = "PARTENAIRE", "Partenaire"
        FONDS_PROPRES = "FONDS_PROPRES", "Fonds Propres"
        CAMPAGNE = "CAMPAGNE", "Campagne"
        AUTRE = "AUTRE", "Autre"

    class Status(models.TextChoices):
        PREVU = "PREVU", "Prévu"
        CONFIRME = "CONFIRME", "Confirmé"
        RECU = "RECU", "Reçu"
        ANNULE = "ANNULE", "Annulé"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    reference = models.CharField(max_length=40, unique=True, blank=True)

    budget = models.ForeignKey(
        Budget,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="financements",
    )

    projet = models.ForeignKey(
        "projects.Project",
        on_delete=models.CASCADE,
        related_name="financements",
    )

    campagne = models.ForeignKey(
        "campaigns.Campaign",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="financements",
    )

    bailleur = models.ForeignKey(
        "Bailleur",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="financements",
    )

    montant = models.DecimalField(max_digits=15, decimal_places=2)
    devise = models.CharField(max_length=10, default="XOF")

    type = models.CharField(
        max_length=50,
        choices=TypeFinancement.choices,
        default=TypeFinancement.BAILLEUR,
    )

    date = models.DateField(default=date.today)

    observation = models.TextField(blank=True)

    statut = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.CONFIRME,
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="created_financements",
    )

    def __str__(self):
        return f"{self.reference} - {self.montant} {self.devise}"


# ==========================
# Dépense
# ==========================

class Depense(FinanceOwnedModel):

    class Status(models.TextChoices):
        EN_ATTENTE = "EN_ATTENTE", "En attente"
        VERIFIE = "VERIFIE", "Vérifié"
        APPROUVE = "APPROUVE", "Approuvé"
        REJETE = "REJETE", "Rejeté"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    reference = models.CharField(max_length=40, unique=True, blank=True)

    budget = models.ForeignKey(
        Budget,
        on_delete=models.PROTECT,
        related_name="depenses",
        null=True,
        blank=True,
    )

    projet = models.ForeignKey(
        "projects.Project",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="depenses",
    )

    ligne_budgetaire = models.ForeignKey(
        LigneBudgetaire,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="depenses",
    )

    campagne = models.ForeignKey(
        "campaigns.Campaign",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="depenses",
    )

    categorie = models.CharField(max_length=100)

    fournisseur = models.CharField(max_length=255, blank=True)

    montant = models.DecimalField(max_digits=15, decimal_places=2)
    devise = models.CharField(max_length=10, default="XOF")

    date = models.DateField(default=date.today)

    description = models.TextField(blank=True)

    statut = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.EN_ATTENTE,
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="created_depenses",
    )

    def __str__(self):
        return self.reference


# ==========================
# Justification
# ==========================

class Justification(models.Model):

    class Status(models.TextChoices):
        CONFORME = "CONFORME", "Conforme"
        A_VERIFIER = "A_VERIFIER", "À vérifier"
        NON_CONFORME = "NON_CONFORME", "Non conforme"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    depense = models.ForeignKey(
        Depense,
        on_delete=models.CASCADE,
        related_name="justifications",
    )

    fichier = models.FileField(upload_to="justifications/")

    type_fichier = models.CharField(max_length=20)

    statut = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.A_VERIFIER,
    )

    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
    )

    valide_par = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="justifications_validees",
    )

    date_validation = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Justification {self.depense.reference}"


# ==========================
# Signaux
# ==========================

@receiver(pre_save, sender=Don)
def generate_don_reference(sender, instance, **kwargs):
    if not instance.reference:
        instance.reference = (
            f"DON-{instance.date.year}-{uuid.uuid4().hex[:8].upper()}"
        )


@receiver(pre_save, sender=Financement)
def generate_financement_reference(sender, instance, **kwargs):
    if not instance.reference:
        instance.reference = (
            f"FIN-{instance.date.year}-{uuid.uuid4().hex[:8].upper()}"
        )


@receiver(pre_save, sender=Depense)
def generate_depense_reference(sender, instance, **kwargs):
    if not instance.reference:
        instance.reference = (
            f"DEP-{instance.date.year}-{uuid.uuid4().hex[:8].upper()}"
        )


@receiver(post_delete, sender=Justification)
def delete_justification_file(sender, instance, **kwargs):
    if instance.fichier:
        instance.fichier.delete(save=False)


@receiver(post_save, sender=Justification)
def auto_validate_depense_on_justification(sender, instance, created, **kwargs):
    """Quand une justification est ajoutée, passer la dépense en VERIFIE si EN_ATTENTE."""
    if created and instance.depense:
        depense = instance.depense
        if depense.statut == Depense.Status.EN_ATTENTE:
            depense.statut = Depense.Status.VERIFIE
            depense.save(update_fields=["statut"])


# ==========================
# Bailleur
# ==========================

class Bailleur(FinanceOwnedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nom = models.CharField(max_length=255)
    type = models.CharField(max_length=100, blank=True)
    email = models.EmailField(blank=True)
    telephone = models.CharField(max_length=50, blank=True)
    adresse = models.TextField(blank=True)
    actif = models.BooleanField(default=True)

    def __str__(self):
        return self.nom


# ==========================
# Partenaire
# ==========================

class Partenaire(FinanceOwnedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nom = models.CharField(max_length=255)
    domaine = models.CharField(max_length=100, blank=True)
    email = models.EmailField(blank=True)
    telephone = models.CharField(max_length=50, blank=True)
    adresse = models.TextField(blank=True)
    actif = models.BooleanField(default=True)

    def __str__(self):
        return self.nom
