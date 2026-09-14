from rest_framework import generics, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from drf_spectacular.utils import extend_schema

from .models import Organization
from .serializers import (
    OrganizationSerializer,
    RegisterOrganizationSerializer,
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

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        organization = serializer.save()

        return Response(
            {
                "message": "Votre ONG a été enregistrée avec succès.",
                "organization": {
                    "id": organization.id,
                    "name": organization.name,
                    "status": organization.status,
                },
                "gerant": {
                    "email": request.data["manager_email"],
                    "status": "INVITED",
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