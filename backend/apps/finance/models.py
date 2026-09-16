import uuid

from django.conf import settings
from django.db import models
from django.db.models.signals import post_delete
from django.dispatch import receiver


class OrganizationOwnedModel(models.Model):
	organization = models.ForeignKey(
		"organizations.Organization",
		on_delete=models.CASCADE,
		related_name="%(app_label)s_%(class)s_set",
	)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		abstract = True


class Bailleur(OrganizationOwnedModel):
	id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
	nom = models.CharField(max_length=200)
	type = models.CharField(max_length=100, blank=True)
	email = models.EmailField(blank=True)
	telephone = models.CharField(max_length=30, blank=True)
	adresse = models.CharField(max_length=255, blank=True)
	logo = models.ImageField(upload_to="bailleurs/logos/", blank=True, null=True)
	actif = models.BooleanField(default=True)
	created_by = models.ForeignKey(
		settings.AUTH_USER_MODEL,
		on_delete=models.SET_NULL,
		null=True,
		related_name="created_bailleurs",
	)


class Partenaire(OrganizationOwnedModel):
	id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
	nom = models.CharField(max_length=200)
	domaine = models.CharField(max_length=150, blank=True)
	email = models.EmailField(blank=True)
	telephone = models.CharField(max_length=30, blank=True)
	adresse = models.CharField(max_length=255, blank=True)
	logo = models.ImageField(upload_to="partenaires/logos/", blank=True, null=True)
	actif = models.BooleanField(default=True)
	created_by = models.ForeignKey(
		settings.AUTH_USER_MODEL,
		on_delete=models.SET_NULL,
		null=True,
		related_name="created_partenaires",
	)


class Don(OrganizationOwnedModel):
	class Status(models.TextChoices):
		PROMIS = "PROMIS", "Promis"
		RECU = "RECU", "Reçu"
		CLOTURE = "CLOTURE", "Clôturé"

	id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
	reference = models.CharField(max_length=40, unique=True, blank=True)
	bailleur = models.ForeignKey(Bailleur, on_delete=models.PROTECT, related_name="dons")
	projet = models.ForeignKey(
		"projects.Project", on_delete=models.SET_NULL, null=True, blank=True, related_name="dons"
	)
	montant = models.DecimalField(max_digits=14, decimal_places=2)
	devise = models.CharField(max_length=10, default="XOF")
	date_reception = models.DateField()
	description = models.TextField(blank=True)
	statut = models.CharField(max_length=20, choices=Status.choices, default=Status.RECU)
	montant_affecte = models.DecimalField(max_digits=14, decimal_places=2, default=0)

	@property
	def montant_restant(self):
		return self.montant - self.montant_affecte

	def save(self, *args, **kwargs):
		if not self.reference:
			self.reference = f"DON-{self.date_reception.year}-{uuid.uuid4().hex[:8].upper()}"
		super().save(*args, **kwargs)


class Budget(OrganizationOwnedModel):
	class Status(models.TextChoices):
		BROUILLON = "BROUILLON", "Brouillon"
		EN_COURS = "EN_COURS", "En cours"
		APPROUVE = "APPROUVE", "Approuvé"
		CLOTURE = "CLOTURE", "Clôturé"

	id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
	projet = models.ForeignKey("projects.Project", on_delete=models.PROTECT, related_name="budgets")
	don = models.ForeignKey(Don, on_delete=models.PROTECT, related_name="budgets")
	montant_total = models.DecimalField(max_digits=14, decimal_places=2)
	statut = models.CharField(max_length=20, choices=Status.choices, default=Status.BROUILLON)
	created_by = models.ForeignKey(
		settings.AUTH_USER_MODEL,
		on_delete=models.SET_NULL,
		null=True,
		related_name="created_budgets",
	)


class PosteBudgetaire(models.Model):
	id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
	budget = models.ForeignKey(Budget, on_delete=models.CASCADE, related_name="postes")
	libelle = models.CharField(max_length=200)
	montant = models.DecimalField(max_digits=14, decimal_places=2)
	montant_depense = models.DecimalField(max_digits=14, decimal_places=2, default=0)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	@property
	def montant_restant(self):
		return self.montant - self.montant_depense


class Depense(OrganizationOwnedModel):
	class Status(models.TextChoices):
		EN_ATTENTE = "EN_ATTENTE", "En attente"
		A_VERIFIER = "A_VERIFIER", "À vérifier"
		APPROUVEE = "APPROUVEE", "Approuvée"
		EXCEPTION = "EXCEPTION", "Exception"
		REJETEE = "REJETEE", "Rejetée"

	id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
	reference = models.CharField(max_length=40, unique=True, blank=True)
	projet = models.ForeignKey("projects.Project", on_delete=models.PROTECT, related_name="depenses")
	poste_budgetaire = models.ForeignKey(PosteBudgetaire, on_delete=models.PROTECT, related_name="depenses")
	libelle = models.CharField(max_length=255)
	montant = models.DecimalField(max_digits=14, decimal_places=2)
	date_depense = models.DateField()
	statut = models.CharField(max_length=20, choices=Status.choices, default=Status.EN_ATTENTE)
	created_by = models.ForeignKey(
		settings.AUTH_USER_MODEL,
		on_delete=models.SET_NULL,
		null=True,
		related_name="created_depenses",
	)

	def save(self, *args, **kwargs):
		if not self.reference:
			self.reference = f"DEP-{self.date_depense.year}-{uuid.uuid4().hex[:8].upper()}"
		super().save(*args, **kwargs)


class Justificatif(models.Model):
	depense = models.ForeignKey(Depense, on_delete=models.CASCADE, related_name="justificatifs")
	fichier = models.FileField(upload_to="justificatifs/")
	nom_original = models.CharField(max_length=255)
	type_fichier = models.CharField(max_length=20)
	taille = models.PositiveIntegerField()
	uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
	created_at = models.DateTimeField(auto_now_add=True)


@receiver(post_delete, sender=Justificatif)
def delete_justificatif_file(sender, instance, **kwargs):
	if instance.fichier:
		instance.fichier.delete(save=False)
