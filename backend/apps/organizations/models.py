import uuid
from django.db import models


class Organization(models.Model):

    class Status(models.TextChoices):
        EN_ATTENTE = "EN_ATTENTE", "En attente"
        ACTIVE = "ACTIVE", "Active"
        REJETEE = "REJETEE", "Rejetée"
        SUSPENDED = "SUSPENDED", "Suspendue"

    name = models.CharField(max_length=200)
    acronym = models.CharField(max_length=50, blank=True)

    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20)

    address = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    region = models.CharField(max_length=100)
    country = models.CharField(max_length=100, default="Sénégal")

    intervention_domain = models.CharField(max_length=150)

    logo = models.ImageField(
        upload_to="organizations/logos/",
        blank=True,
        null=True
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.EN_ATTENTE
    )

    is_active = models.BooleanField(default=False)

    # Documents d'inscription
    document_receipt = models.FileField(upload_to="organizations/documents/receipts/", blank=True, null=True)
    document_ninea = models.FileField(upload_to="organizations/documents/ninea/", blank=True, null=True)
    document_statutes = models.FileField(upload_to="organizations/documents/statutes/", blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Subscription(models.Model):

    class Status(models.TextChoices):
        TRIAL = "TRIAL", "Essai gratuit"
        ACTIVE = "ACTIVE", "Active"
        EXPIRE = "EXPIRE", "Expirée"

    organization = models.OneToOneField(Organization, on_delete=models.CASCADE, related_name="subscription")
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.TRIAL)
    trial_start = models.DateField(null=True, blank=True)
    trial_end = models.DateField(null=True, blank=True)
    started_at = models.DateTimeField(null=True, blank=True)
    ended_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Subscription - {self.organization.name}"


class OrganisationRequest(models.Model):
    """
    Demande d'inscription d'une ONG.
    Le gérant soumet les informations + 3 documents PDF.
    Le rapport IA est purement consultatif.
    La décision finale appartient au Super Administrateur.
    """

    class Statut(models.TextChoices):
        EN_ATTENTE = "EN_ATTENTE", "En attente"
        APPROUVEE = "APPROUVEE", "Approuvée"
        REJETEE = "REJETEE", "Rejetée"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Informations ONG
    nom_ong = models.CharField("Nom de l'ONG", max_length=255)
    sigle = models.CharField("Sigle", max_length=50, blank=True)
    domaine = models.CharField("Domaine d'intervention", max_length=200, blank=True)
    region = models.CharField("Région", max_length=100, blank=True)
    adresse = models.CharField("Adresse", max_length=255, blank=True)
    email = models.EmailField("Email de contact")
    telephone = models.CharField("Téléphone", max_length=30)

    # Gérant
    gerant_prenom = models.CharField("Prénom du gérant", max_length=100)
    gerant_nom = models.CharField("Nom du gérant", max_length=100)
    gerant_email = models.EmailField("Email du gérant")
    gerant_telephone = models.CharField("Téléphone du gérant", max_length=30, blank=True)

    # Documents PDF
    recepisse_pdf = models.FileField(
        "Récépissé (PDF)",
        upload_to="organisation_requests/recepisse/",
    )
    ninea_pdf = models.FileField(
        "NINEA (PDF)",
        upload_to="organisation_requests/ninea/",
    )
    statuts_pdf = models.FileField(
        "Statuts (PDF)",
        upload_to="organisation_requests/statuts/",
    )

    # Statut
    statut = models.CharField(
        max_length=20,
        choices=Statut.choices,
        default=Statut.EN_ATTENTE,
    )

    # Rapport IA (stocké en JSON pour accès direct)
    ai_report = models.JSONField("Rapport IA", default=dict, blank=True)

    # Motif de rejet (si applicable)
    motif_rejet = models.TextField("Motif de rejet", blank=True)

    # Lien vers l'organisation créée (une fois approuvée)
    organization = models.ForeignKey(
        Organization,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="requests",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Demande d'inscription ONG"
        verbose_name_plural = "Demandes d'inscription ONG"

    def __str__(self):
        return f"{self.nom_ong} — {self.get_statut_display()}"


class AIVerificationReport(models.Model):
    """
    Rapport de pré-vérification IA pour une demande d'inscription.
    Stocke le résultat OCR + LLM.
    Ce rapport est uniquement consultatif.
    """

    class StatutIA(models.TextChoices):
        A_VERIFIER = "A_VERIFIER", "À vérifier"
        CONFORME = "CONFORME", "Conforme"
        NON_CONFORME = "NON_CONFORME", "Non conforme"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    request = models.OneToOneField(
        OrganisationRequest,
        on_delete=models.CASCADE,
        related_name="verification_report",
    )

    score_confiance = models.IntegerField("Score de confiance (%)", default=0)
    statut_ia = models.CharField(
        max_length=20,
        choices=StatutIA.choices,
        default=StatutIA.A_VERIFIER,
    )

    # Informations extraites par OCR
    nom_extrait = models.CharField("Nom extrait (OCR)", max_length=255, blank=True)
    ninea_extrait = models.CharField("NINEA extrait", max_length=100, blank=True)
    recepisse_extrait = models.CharField("N° récépissé extrait", max_length=100, blank=True)

    # Vérification des documents (JSON array)
    documents = models.JSONField("État des documents", default=list)

    # Observations et recommandations
    observation = models.TextField("Observation IA", blank=True)
    recommandation = models.TextField("Recommandation", blank=True)

    # Anomalies détectées (JSON array)
    anomalies = models.JSONField("Anomalies détectées", default=list)

    # Rapport brut complet de l'IA
    raw_response = models.JSONField("Réponse brute IA", default=dict)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Rapport de vérification IA"
        verbose_name_plural = "Rapports de vérification IA"

    def __str__(self):
        return f"Rapport IA — {self.request.nom_ong} ({self.score_confiance}%)"

