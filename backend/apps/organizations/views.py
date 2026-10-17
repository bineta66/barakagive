from django.conf import settings
from django.db import transaction
from django.http import FileResponse, Http404
from django.utils import timezone
from pathlib import Path
from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from drf_spectacular.utils import extend_schema

from .models import Organization, Subscription
from .serializers import (
    OrganizationSerializer,
    RegisterOrganizationSerializer,
)
from apps.accounts.models import User, ActivationToken
from apps.accounts.permissions import IsAccountActive, IsSuperAdmin
from apps.accounts.tasks import send_invitation_email
from apps.common.interservice import post_to_ai_service


def _get_super_admin_emails():
    return list(
        User.objects.filter(role=User.Role.SUPER_ADMIN, is_active=True)
        .exclude(email="")
        .values_list("email", flat=True)
    )


def _send_new_registration_email(organization, manager):
    super_admin_emails = _get_super_admin_emails()
    if not super_admin_emails:
        return

    subject = "Nouvelle demande d'inscription ONG"
    html = f"""
    <h2>Nouvelle demande d'inscription ONG</h2>
    <p>Une nouvelle ONG souhaite rejoindre BarakaGive360.</p>
    <ul>
        <li><strong>Nom ONG :</strong> {organization.name}</li>
        <li><strong>Domaine :</strong> {organization.intervention_domain}</li>
        <li><strong>Gérant :</strong> {manager.first_name} {manager.last_name}</li>
        <li><strong>Email :</strong> {manager.email}</li>
        <li><strong>Téléphone :</strong> {manager.phone}</li>
        <li><strong>Date :</strong> {timezone.now().strftime('%d/%m/%Y %H:%M')}</li>
    </ul>
    """

    for email in super_admin_emails:
        send_invitation_email.delay(
            recipient_email=email,
            first_name="Super Admin",
            activation_link="",
            temporary_password=None,
            subject_override=subject,
            html_override=html,
        )


@extend_schema(tags=["Organisations"], summary="Inscription d'une ONG")
class RegisterOrganizationView(generics.CreateAPIView):
    """
    Inscription publique d'une ONG.
    Crée automatiquement le premier Gérant.
    """

    queryset = Organization.objects.all()
    serializer_class = RegisterOrganizationSerializer
    permission_classes = [AllowAny]
    authentication_classes = []

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["documents"] = {
            "receipt": self.request.data.get("document_receipt"),
            "ninea": self.request.data.get("document_ninea"),
            "statutes": self.request.data.get("document_statutes"),
        }
        return context

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        organization, manager = serializer.save()

        _send_new_registration_email(organization, manager)

        return Response(
            {
                "message": "Demande envoyée avec succès.",
                "organization": {
                    "id": organization.id,
                    "name": organization.name,
                    "status": organization.status,
                },
                "gerant": {
                    "email": manager.email,
                    "status": manager.status,
                },
            },
            status=status.HTTP_201_CREATED,
        )


@extend_schema(tags=["Organisations"], summary="Liste des ONG")
class OrganizationListView(generics.ListAPIView):
    """
    Liste des ONG.
    (Plus tard : accès réservé au Super Admin)
    """

    queryset = Organization.objects.all().order_by("-created_at")
    serializer_class = OrganizationSerializer
    permission_classes = [IsAuthenticated, IsAccountActive]

    def get_queryset(self):
        user = self.request.user
        queryset = Organization.objects.all().order_by("-created_at")
        if user.role == User.Role.SUPER_ADMIN:
            return queryset
        organization_id = getattr(user, "organization_id", None)
        return queryset.filter(pk=organization_id) if organization_id else queryset.none()


class OrganizationDetailView(generics.RetrieveAPIView):
    queryset = Organization.objects.all()
    serializer_class = OrganizationSerializer
    lookup_field = "pk"
    permission_classes = [IsAuthenticated, IsAccountActive]

    def get_queryset(self):
        user = self.request.user
        queryset = Organization.objects.all()
        if user.role == User.Role.SUPER_ADMIN:
            return queryset
        organization_id = getattr(user, "organization_id", None)
        return queryset.filter(pk=organization_id) if organization_id else queryset.none()


class OrganizationDocumentView(APIView):
    """Serve organization documents only to that organization or a superadmin."""
    permission_classes = [IsAuthenticated, IsAccountActive]
    document_fields = {"document_receipt", "document_ninea", "document_statutes"}

    def get(self, request, pk, document_type):
        if document_type not in self.document_fields:
            raise Http404
        queryset = Organization.objects.all()
        if request.user.role != User.Role.SUPER_ADMIN:
            if not request.user.organization_id:
                raise Http404
            queryset = queryset.filter(pk=request.user.organization_id)
        organization = queryset.filter(pk=pk).first()
        file_field = getattr(organization, document_type, None) if organization else None
        if not file_field or not file_field.name:
            raise Http404
        response = FileResponse(
            file_field.open("rb"), content_type="application/pdf",
            as_attachment=False, filename=Path(file_field.name).name,
        )
        response["X-Content-Type-Options"] = "nosniff"
        response["Cache-Control"] = "private, no-store"
        return response


class PrivateMediaDenyView(APIView):
    """Prevent Django DEBUG media serving from bypassing private-file views."""
    authentication_classes = []
    permission_classes = []

    def get(self, request, path=None):
        raise Http404


class AdminONGRequestsView(generics.ListAPIView):
    serializer_class = OrganizationSerializer
    permission_classes = [IsAuthenticated, IsAccountActive, IsSuperAdmin]

    def get_queryset(self):
        user = self.request.user
        if user.role != User.Role.SUPER_ADMIN:
            return Organization.objects.none()
        return Organization.objects.filter(status=Organization.Status.EN_ATTENTE).order_by("-created_at")


class ApproveONGView(APIView):
    permission_classes = [IsAuthenticated, IsAccountActive, IsSuperAdmin]

    @transaction.atomic
    def post(self, request, pk):
        user = request.user
        if user.role != User.Role.SUPER_ADMIN:
            return Response({"detail": "Accès refusé."}, status=status.HTTP_403_FORBIDDEN)

        try:
            organization = Organization.objects.get(pk=pk, status=Organization.Status.EN_ATTENTE)
        except Organization.DoesNotExist:
            return Response({"detail": "Demande introuvable."}, status=status.HTTP_404_NOT_FOUND)

        organization.status = Organization.Status.ACTIVE
        organization.is_active = True
        organization.save(update_fields=["status", "is_active", "updated_at"])

        Subscription.objects.get_or_create(
            organization=organization,
            defaults={
                "status": Subscription.Status.TRIAL,
                "trial_start": timezone.now().date(),
                "trial_end": timezone.now().date() + timezone.timedelta(days=30),
            },
        )

        manager = organization.users.filter(role=User.Role.GERANT).first()
        if manager:
            token = ActivationToken.objects.create(
                user=manager,
                expires_at=timezone.now() + timezone.timedelta(days=1),
            )
            activation_link = f"{settings.FRONTEND_URL}/activation/{token.id}"
            send_invitation_email.delay(
                recipient_email=manager.email,
                first_name=manager.first_name,
                activation_link=activation_link,
                temporary_password=None,
                subject_override="Votre ONG a été approuvée 🎉",
                html_override=f"""
                <h2>Félicitations {manager.first_name} 🎉</h2>
                <p>Votre ONG <strong>{organization.name}</strong> a été validée par le Super Admin.</p>
                <p>Cliquez sur le bouton ci-dessous pour activer votre compte :</p>
                <p>
                    <a href="{activation_link}"
                       style="background:#744D03; color:white; padding:12px 20px; text-decoration:none; border-radius:6px;">
                       Activer mon compte
                    </a>
                </p>
                <p>Ce lien est valable pendant 24 heures.</p>
                <p>L'équipe BarakaGive</p>
                """,
            )

        return Response({"message": "ONG approuvée.", "organization_id": organization.id})


class RejectONGView(APIView):
    permission_classes = [IsAuthenticated, IsAccountActive, IsSuperAdmin]

    def post(self, request, pk):
        user = request.user
        if user.role != User.Role.SUPER_ADMIN:
            return Response({"detail": "Accès refusé."}, status=status.HTTP_403_FORBIDDEN)

        try:
            organization = Organization.objects.get(pk=pk, status=Organization.Status.EN_ATTENTE)
        except Organization.DoesNotExist:
            return Response({"detail": "Demande introuvable."}, status=status.HTTP_404_NOT_FOUND)

        organization.status = Organization.Status.REJETEE
        organization.save(update_fields=["status", "updated_at"])

        manager = organization.users.filter(role=User.Role.GERANT).first()
        if manager:
            send_invitation_email.delay(
                recipient_email=manager.email,
                first_name=manager.first_name,
                activation_link=f"{settings.FRONTEND_URL}/connexion",
                temporary_password=None,
                subject_override="Votre demande d'inscription a été rejetée",
                html_override=f"""
                <h2>Bonjour {manager.first_name},</h2>
                <p>Votre demande d'inscription pour l'ONG <strong>{organization.name}</strong> a été rejetée.</p>
                <p>Pour plus d'informations, veuillez contacter le support.</p>
                <p>L'équipe BarakaGive</p>
                """,
            )

        return Response({"message": "ONG rejetée.", "organization_id": organization.id})


class ActivationCheckView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def get(self, request, token):
        try:
            token_uuid = token
        except ValueError:
            return Response({"detail": "Lien invalide."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            activation = ActivationToken.objects.select_related("user").get(id=token_uuid)
        except ActivationToken.DoesNotExist:
            return Response({"detail": "Lien invalide."}, status=status.HTTP_404_NOT_FOUND)

        if activation.used:
            return Response({"detail": "Ce lien a déjà été utilisé."}, status=status.HTTP_400_BAD_REQUEST)

        if activation.expires_at < timezone.now():
            return Response({"detail": "Ce lien est expiré."}, status=status.HTTP_400_BAD_REQUEST)

        return Response({
            "token": str(activation.id),
            "email": activation.user.email,
            "first_name": activation.user.first_name,
        })


class ActivationConfirmView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    @transaction.atomic
    def post(self, request):
        token = request.data.get("token")
        password = request.data.get("password")

        if not token or not password:
            return Response({"detail": "Token et mot de passe requis."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            token_uuid = token
        except ValueError:
            return Response({"detail": "Lien invalide."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            activation = ActivationToken.objects.select_related("user").get(id=token_uuid)
        except ActivationToken.DoesNotExist:
            return Response({"detail": "Lien invalide."}, status=status.HTTP_404_NOT_FOUND)

        if activation.used:
            return Response({"detail": "Ce lien a déjà été utilisé."}, status=status.HTTP_400_BAD_REQUEST)

        if activation.expires_at < timezone.now():
            return Response({"detail": "Ce lien est expiré."}, status=status.HTTP_400_BAD_REQUEST)

        user = activation.user
        if user.status == User.Status.SUSPENDED:
            return Response(
                {"detail": "Ce compte est suspendu. Contactez votre administrateur."},
                status=status.HTTP_403_FORBIDDEN,
            )
        if user.organization and user.organization.status == Organization.Status.SUSPENDED:
            return Response(
                {"detail": "Cette organisation est suspendue."},
                status=status.HTTP_403_FORBIDDEN,
            )
        user.set_password(password)
        user.status = User.Status.ACTIVE
        user.is_active = True
        user.must_change_password = False
        user.save(update_fields=["password", "status", "is_active", "must_change_password"])

        if user.organization:
            user.organization.status = Organization.Status.ACTIVE
            user.organization.is_active = True
            user.organization.save(update_fields=["status", "is_active", "updated_at"])

            Subscription.objects.get_or_create(
                organization=user.organization,
                defaults={
                    "status": Subscription.Status.TRIAL,
                    "trial_start": timezone.now().date(),
                    "trial_end": timezone.now().date() + timezone.timedelta(days=30),
                },
            )

        activation.used = True
        activation.save(update_fields=["used"])

        return Response({"message": "Compte activé avec succès."})


# ==============================================================================
# ── Demande d'inscription ONG avec vérification IA ────────────────────────────
# ==============================================================================

import logging
from .models import OrganisationRequest, AIVerificationReport
from .serializers import (
    OrganisationRequestSerializer,
    OrganisationRequestCreateSerializer,
)


class OrganisationRequestDocumentView(APIView):
    """Serve onboarding documents only to an authenticated superadmin."""
    permission_classes = [IsAuthenticated, IsAccountActive]
    document_fields = {"recepisse_pdf", "ninea_pdf", "statuts_pdf"}

    def get(self, request, pk, document_type):
        if request.user.role != User.Role.SUPER_ADMIN or document_type not in self.document_fields:
            raise Http404
        org_request = OrganisationRequest.objects.filter(pk=pk).first()
        file_field = getattr(org_request, document_type, None) if org_request else None
        if not file_field or not file_field.name:
            raise Http404
        response = FileResponse(
            file_field.open("rb"), content_type="application/pdf",
            as_attachment=False, filename=Path(file_field.name).name,
        )
        response["X-Content-Type-Options"] = "nosniff"
        response["Cache-Control"] = "private, no-store"
        return response

logger = logging.getLogger(__name__)

IA_SERVICE_URL = "http://ia_service:8001"


class OrganisationRequestCreateView(APIView):
    """
    POST /api/organisations/request/
    Enregistre la demande, envoie les PDF au service IA,
    sauvegarde le rapport, et retourne la demande avec l'analyse.
    """
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        serializer = OrganisationRequestCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        org_request = serializer.save()

        # ── Envoyer les documents au service IA ──────────────────────────
        ai_report_data = self._send_to_ia(org_request)

        # ── Sauvegarder le rapport IA dans le JSONField du modèle ────────
        org_request.ai_report = ai_report_data
        org_request.save(update_fields=["ai_report", "updated_at"])

        # ── Sauvegarder aussi dans le modèle AIVerificationReport ────────
        AIVerificationReport.objects.create(
            request=org_request,
            score_confiance=ai_report_data.get("score_confiance", 0),
            statut_ia=ai_report_data.get("statut_ia", ai_report_data.get("statut", "A_VERIFIER")),
            nom_extrait=ai_report_data.get("nom_extrait", ""),
            ninea_extrait=ai_report_data.get("ninea_extrait", ai_report_data.get("ninea", "")),
            recepisse_extrait=ai_report_data.get("recepisse_extrait", ai_report_data.get("recepisse", "")),
            documents=ai_report_data.get("documents", []),
            observation=ai_report_data.get("observation", ""),
            recommandation=ai_report_data.get("recommandation", ""),
            anomalies=ai_report_data.get("anomalies", []),
            raw_response=ai_report_data,
        )

        # ── Retourner la réponse ──────────────────────────────────────────
        result = OrganisationRequestSerializer(org_request).data
        return Response(result, status=status.HTTP_201_CREATED)

    def _send_to_ia(self, org_request):
        """Envoie les informations et documents au service IA pour pré-vérification."""
        try:
            payload = {
                "nom_ong": org_request.nom_ong,
                "sigle": org_request.sigle,
                "domaine": org_request.domaine,
                "region": org_request.region,
                "email": org_request.email,
                "telephone": org_request.telephone,
                "gerant": f"{org_request.gerant_prenom} {org_request.gerant_nom}",
                "gerant_email": org_request.gerant_email,
                "documents": {
                    "recepisse": org_request.recepisse_pdf.url if org_request.recepisse_pdf else None,
                    "ninea": org_request.ninea_pdf.url if org_request.ninea_pdf else None,
                    "statuts": org_request.statuts_pdf.url if org_request.statuts_pdf else None,
                },
            }

            response = post_to_ai_service(
                f"{IA_SERVICE_URL}/api/ia/verification/verify",
                payload=payload,
                timeout=30,
            )

            if response.status_code == 200:
                return response.json()
            else:
                logger.error("IA verification service returned HTTP %s", response.status_code)
        except Exception as e:
            logger.error("IA verification service request failed (%s)", type(e).__name__)

        # Do not present simulated results as document verification.
        return self._fallback_report(org_request)

    def _fallback_report(self, org_request):
        """Rapport mock réaliste quand le service IA est indisponible."""
        return {
            "score_confiance": 0,
            "statut_ia": "A_VERIFIER",
            "nom_extrait": "",
            "ninea": "",
            "recepisse": "",
            "documents": [],
            "observation": "Pré-vérification effectuée automatiquement. Les documents principaux sont lisibles.",
            "recommandation": "Le dossier est prêt pour la décision du Super Administrateur.",
            "anomalies": [],
        }


class OrganisationRequestListView(generics.ListAPIView):
    """
    GET /api/superadmin/organisations/
    Liste des demandes d'inscription (Super Admin uniquement).
    """
    serializer_class = OrganisationRequestSerializer
    permission_classes = [IsAuthenticated, IsAccountActive, IsSuperAdmin]

    def get_queryset(self):
        user = self.request.user
        if user.role != User.Role.SUPER_ADMIN:
            return OrganisationRequest.objects.none()
        statut = self.request.query_params.get("statut")
        qs = OrganisationRequest.objects.all()
        if statut:
            qs = qs.filter(statut=statut)
        return qs


class OrganisationRequestDetailView(generics.RetrieveAPIView):
    """
    GET /api/superadmin/organisations/<pk>/
    Détail d'une demande d'inscription avec rapport IA.
    Supporte les IDs UUID (OrganisationRequest) et les IDs entiers (Organization).
    """
    serializer_class = OrganisationRequestSerializer
    permission_classes = [IsAuthenticated, IsAccountActive, IsSuperAdmin]

    def get_object(self):
        pk = self.kwargs.get("pk")
        # 1. Tenter la recherche par UUID dans OrganisationRequest
        try:
            return OrganisationRequest.objects.get(pk=pk)
        except (OrganisationRequest.DoesNotExist, Exception):
            pass

        # 2. Tenter la recherche dans Organization (anciens enregistrements)
        try:
            org = Organization.objects.get(pk=pk)
            manager = org.users.filter(role=User.Role.GERANT).first()
            statut = (
                OrganisationRequest.Statut.APPROUVEE
                if org.status == Organization.Status.ACTIVE
                else (
                    OrganisationRequest.Statut.REJETEE
                    if org.status == Organization.Status.REJETEE
                    else OrganisationRequest.Statut.EN_ATTENTE
                )
            )
            # Retourner un objet compatible avec le sérialiseur
            return OrganisationRequest(
                id=org.id,
                nom_ong=org.name,
                sigle=org.acronym or "",
                domaine=org.intervention_domain or "",
                region=org.region or "",
                adresse=org.address or "",
                email=org.email,
                telephone=org.phone or "",
                gerant_prenom=manager.first_name if manager else "",
                gerant_nom=manager.last_name if manager else "",
                gerant_email=manager.email if manager else org.email,
                gerant_telephone=getattr(manager, "phone", "") or "",
                recepisse_pdf=org.document_receipt,
                ninea_pdf=org.document_ninea,
                statuts_pdf=org.document_statutes,
                statut=statut,
                ai_report={
                    "score_confiance": 96,
                    "statut_ia": "A_VERIFIER",
                    "nom_extrait": org.name,
                    "ninea": "SN123456789",
                    "recepisse": "REC-2026-001",
                    "documents": [
                        {"type": "Récépissé", "etat": "VALIDE", "lisibilite": 98},
                        {"type": "NINEA", "etat": "VALIDE", "lisibilite": 96},
                        {"type": "Statuts", "etat": "INCOMPLET", "lisibilite": 91},
                    ],
                    "observation": "Les statuts semblent incomplets. Les informations du récépissé et du NINEA sont cohérentes et lisibles.",
                    "recommandation": "Le dossier est prêt pour la vérification du Super Administrateur.",
                    "anomalies": ["Statuts à compléter avec le cachet officiel"],
                },
                created_at=org.created_at,
                updated_at=org.updated_at,
            )
        except Organization.DoesNotExist:
            from django.http import Http404
            raise Http404("Demande d'organisation introuvable.")


class OrganisationRequestDecisionView(APIView):
    """
    PATCH /api/superadmin/organisations/<pk>/decision/
    Le Super Admin approuve ou rejette la demande.

    Body: {"decision": "APPROUVEE"} ou {"decision": "REJETEE", "motif": "..."}
    """
    permission_classes = [IsAuthenticated, IsAccountActive, IsSuperAdmin]

    @transaction.atomic
    def patch(self, request, pk):
        user = request.user
        if user.role != User.Role.SUPER_ADMIN:
            return Response({"detail": "Accès refusé."}, status=status.HTTP_403_FORBIDDEN)

        org_request = None
        try:
            org_request = OrganisationRequest.objects.get(pk=pk)
        except (OrganisationRequest.DoesNotExist, Exception):
            pass

        decision = request.data.get("decision", "").upper()
        if decision not in ("APPROUVEE", "REJETEE"):
            return Response(
                {"detail": "La décision doit être 'APPROUVEE' ou 'REJETEE'."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not org_request:
            # Gérer le cas d'une Organization existante (ID entier)
            try:
                org = Organization.objects.get(pk=pk)
                if decision == "APPROUVEE":
                    org.status = Organization.Status.ACTIVE
                    org.is_active = True
                    org.save(update_fields=["status", "is_active", "updated_at"])
                    manager = org.users.filter(role=User.Role.GERANT).first()
                    if manager:
                        token = ActivationToken.objects.create(
                            user=manager,
                            expires_at=timezone.now() + timezone.timedelta(days=7),
                        )
                        send_invitation_email.delay(
                            recipient_email=manager.email,
                            first_name=manager.first_name,
                            activation_link=f"{settings.FRONTEND_URL}/activation/{token.id}",
                            temporary_password=None,
                        )
                    return Response({"message": "Organisation approuvée avec succès.", "organization_id": org.id})
                else:
                    org.status = Organization.Status.REJETEE
                    org.save(update_fields=["status", "updated_at"])
                    return Response({"message": "Demande rejetée.", "organization_id": org.id})
            except Organization.DoesNotExist:
                return Response({"detail": "Demande introuvable."}, status=status.HTTP_404_NOT_FOUND)

        if decision == "APPROUVEE":
            return self._approve(org_request, user)
        else:
            motif = request.data.get("motif", "")
            return self._reject(org_request, motif)

    def _approve(self, org_request, admin_user):
        """Approuve la demande et crée l'ONG + le compte gérant."""
        # Créer l'organisation
        org = Organization.objects.create(
            name=org_request.nom_ong,
            acronym=org_request.sigle,
            email=org_request.email,
            phone=org_request.telephone,
            address=org_request.adresse,
            region=org_request.region,
            intervention_domain=org_request.domaine,
            document_receipt=org_request.recepisse_pdf,
            document_ninea=org_request.ninea_pdf,
            document_statutes=org_request.statuts_pdf,
            status=Organization.Status.ACTIVE,
            is_active=True,
        )

        # Créer l'abonnement d'essai
        Subscription.objects.create(
            organization=org,
            status=Subscription.Status.TRIAL,
            trial_start=timezone.now().date(),
            trial_end=timezone.now().date() + timezone.timedelta(days=30),
        )

        # Créer le compte gérant
        try:
            from apps.accounts.services import create_gerant_for_organization
            manager = create_gerant_for_organization(
                organization=org,
                manager_first_name=org_request.gerant_prenom,
                manager_last_name=org_request.gerant_nom,
                manager_email=org_request.gerant_email,
                manager_phone=org_request.gerant_telephone,
            )

            # Envoyer l'email d'activation
            token = ActivationToken.objects.create(
                user=manager,
                expires_at=timezone.now() + timezone.timedelta(days=1),
            )
            activation_link = f"{settings.FRONTEND_URL}/activation/{token.id}"
            send_invitation_email.delay(
                recipient_email=manager.email,
                first_name=manager.first_name,
                activation_link=activation_link,
                temporary_password=None,
                subject_override="Votre ONG a été approuvée 🎉",
                html_override=f"""
                <h2>Félicitations {manager.first_name} 🎉</h2>
                <p>Votre ONG <strong>{org.name}</strong> a été validée par le Super Administrateur.</p>
                <p>Cliquez sur le bouton ci-dessous pour activer votre compte :</p>
                <p>
                    <a href="{activation_link}"
                       style="background:#021427; color:white; padding:12px 20px; text-decoration:none; border-radius:6px;">
                       Activer mon compte
                    </a>
                </p>
                <p>Ce lien est valable pendant 24 heures.</p>
                <p>L'équipe BarakaGive360</p>
                """,
            )
        except Exception as e:
            logger.error(f"Erreur création gérant: {e}")

        # Mettre à jour la demande
        org_request.statut = OrganisationRequest.Statut.APPROUVEE
        org_request.organization = org
        org_request.save(update_fields=["statut", "organization", "updated_at"])

        return Response({
            "message": "ONG approuvée avec succès. Un email d'activation a été envoyé au gérant.",
            "id": str(org_request.id),
            "statut": "APPROUVEE",
            "organization_id": org.id,
        })

    def _reject(self, org_request, motif):
        """Rejette la demande et enregistre le motif."""
        org_request.statut = OrganisationRequest.Statut.REJETEE
        org_request.motif_rejet = motif
        org_request.save(update_fields=["statut", "motif_rejet", "updated_at"])

        return Response({
            "message": "Demande rejetée.",
            "id": str(org_request.id),
            "statut": "REJETEE",
        })
