from calendar import monthrange
from datetime import date, timedelta

from django.db.models import Count
from django.db.models.functions import TruncDate, TruncMonth
from django.utils import timezone
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.models import User
from apps.accounts.permissions import IsAccountActive, IsSuperAdmin
from apps.beneficiaries.models import Beneficiary
from apps.campaigns.models import Campaign
from apps.organizations.models import OrganisationRequest, Organization
from apps.payment.models import Subscription
from apps.projects.models import Project


def _subtract_months(value, months):
    month_index = value.year * 12 + value.month - 1 - months
    year, month_index = divmod(month_index, 12)
    month = month_index + 1
    return date(year, month, min(value.day, monthrange(year, month)[1]))


def _series(queryset, field, start, end, monthly):
    trunc = TruncMonth if monthly else TruncDate
    counts = {
        row["bucket"].date() if hasattr(row["bucket"], "date") else row["bucket"]: row["total"]
        for row in queryset.filter(**{f"{field}__date__gte": start, f"{field}__date__lte": end})
        .annotate(bucket=trunc(field))
        .values("bucket")
        .annotate(total=Count("pk"))
    }
    buckets = []
    if monthly:
        cursor = start.replace(day=1)
        last = end.replace(day=1)
        while cursor <= last:
            buckets.append(cursor)
            cursor = _subtract_months(cursor, -1).replace(day=1)
    else:
        cursor = start
        while cursor <= end:
            buckets.append(cursor)
            cursor += timedelta(days=1)
    key_format = "%Y-%m" if monthly else "%Y-%m-%d"
    return [{"date": bucket.strftime(key_format), "count": counts.get(bucket, 0)} for bucket in buckets]


class SuperAdminDashboardView(APIView):
    permission_classes = [IsAuthenticated, IsAccountActive, IsSuperAdmin]

    def get(self, request):
        today = timezone.localdate()
        period = request.query_params.get("period", "30d")
        period_config = {
            "7d": (timedelta(days=6), False),
            "30d": (timedelta(days=29), False),
            "3m": (None, True),
            "6m": (None, True),
            "1y": (None, True),
        }
        if period not in period_config:
            period = "30d"
        delta, monthly = period_config[period]
        start = today - delta if delta else _subtract_months(today, {"3m": 2, "6m": 5, "1y": 11}[period]).replace(day=1)

        organizations = Organization.objects.all()
        requests = OrganisationRequest.objects.all()
        pending_requests = requests.filter(statut=OrganisationRequest.Statut.EN_ATTENTE)
        pending_organizations = organizations.filter(status=Organization.Status.EN_ATTENTE).exclude(
            requests__statut=OrganisationRequest.Statut.EN_ATTENTE
        ).distinct()
        # Le KPI représente tous les comptes gérant inscrits, y compris ceux
        # qui ne sont pas encore rattachés à une ONG.
        managers = User.objects.filter(role=User.Role.GERANT)
        active_managers = managers.filter(status=User.Status.ACTIVE, is_active=True)
        projects = Project.objects.all()
        campaigns = Campaign.objects.all()
        beneficiaries = Beneficiary.objects.all()
        subscriptions = Subscription.objects.all()

        organization_status_counts = dict(
            organizations.values("status")
            .annotate(total=Count("pk"))
            .values_list("status", "total")
        )
        organization_status = {
            key: organization_status_counts.get(key, 0)
            for key, _ in Organization.Status.choices
        }
        organizations_by_region = list(
            organizations.filter(country__iexact="Sénégal")
            .exclude(region__exact="")
            .values("region")
            .annotate(total=Count("pk"))
            .order_by("region")
        )
        campaign_status = {key: campaigns.filter(statut=key).count() for key, _ in Campaign.Statut.choices}
        project_status = {
            "NON_ARCHIVE": projects.filter(archived=False).count(),
            "ARCHIVE": projects.filter(archived=True).count(),
        }

        recent_projects = list(projects.select_related("organization").order_by("-created_at")[:50].values(
            "id", "code", "name", "organization__name", "archived", "created_at"
        ))
        recent_campaigns = list(campaigns.select_related("projet").order_by("-created_at")[:50].values(
            "id", "nom", "projet__name", "statut", "created_at"
        ))
        activities = []
        for item in requests.order_by("-created_at")[:8].values("nom_ong", "created_at", "gerant_nom", "gerant_prenom"):
            activities.append({"type": "Demande ONG reçue", "sujet": item["nom_ong"], "acteur": f'{item["gerant_prenom"]} {item["gerant_nom"]}'.strip(), "date": item["created_at"]})
        for item in projects.select_related("organization").order_by("-created_at")[:8].values("name", "organization__name", "created_at"):
            activities.append({"type": "Projet créé", "sujet": item["name"], "acteur": item["organization__name"], "date": item["created_at"]})
        for item in campaigns.select_related("organization").order_by("-created_at")[:8].values("nom", "organization__name", "created_at"):
            activities.append({"type": "Campagne créée", "sujet": item["nom"], "acteur": item["organization__name"], "date": item["created_at"]})
        for item in managers.order_by("-date_joined")[:8].values("first_name", "last_name", "organization__name", "date_joined"):
            activities.append({"type": "Gérant inscrit", "sujet": f'{item["first_name"]} {item["last_name"]}'.strip(), "acteur": item["organization__name"], "date": item["date_joined"]})
        for item in beneficiaries.order_by("-created_at")[:8].values("organization__name", "created_at"):
            activities.append({"type": "Bénéficiaire enregistré", "sujet": "Nouveau dossier", "acteur": item["organization__name"], "date": item["created_at"]})
        activities.sort(key=lambda item: item["date"], reverse=True)
        recent_requests = [
            {"id": str(item["id"]), "nom_ong": item["nom_ong"], "email": item["email"], "region": item["region"], "created_at": item["created_at"]}
            for item in pending_requests.order_by("-created_at").values("id", "nom_ong", "email", "region", "created_at")[:8]
        ]
        recent_requests.extend(
            {"id": str(item["id"]), "nom_ong": item["name"], "email": item["email"], "region": item["region"], "created_at": item["created_at"]}
            for item in pending_organizations.order_by("-created_at").values("id", "name", "email", "region", "created_at")[:8]
        )
        recent_requests.sort(key=lambda item: item["created_at"], reverse=True)

        return Response({
            "updated_at": timezone.now(),
            "period": period,
            "ongs": {
                "total": organizations.count(),
                "actives": organizations.filter(status=Organization.Status.ACTIVE).count(),
                "pending": pending_requests.count() + pending_organizations.count(),
                "par_statut": organization_status,
                "par_region": organizations_by_region,
            },
            "demandes_recentes": recent_requests[:8],
            "gerants": {"total": managers.count(), "actifs": active_managers.count()},
            "abonnements": {"actifs": subscriptions.filter(statut=Subscription.Statut.ACTIVE, is_active=True).count()},
            "projets": {"total": projects.count(), "par_statut": project_status, "derniers": recent_projects},
            "campagnes": {"total": campaigns.count(), "par_statut": campaign_status, "dernieres": recent_campaigns},
            "beneficiaires": {"total": beneficiaries.count()},
            "evolution": {
                "projets": _series(projects, "created_at", start, today, monthly),
                "campagnes": _series(campaigns, "created_at", start, today, monthly),
                "beneficiaires": _series(beneficiaries, "created_at", start, today, monthly),
            },
            "activites_recentes": [{**item, "date": item["date"]} for item in activities[:20]],
        })
