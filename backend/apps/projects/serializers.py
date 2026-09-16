from rest_framework import serializers

from apps.accounts.models import User
from .models import Project, ProjectCriteria


class ProjectCriteriaSerializer(serializers.ModelSerializer):

    class Meta:
        model = ProjectCriteria
        fields = "__all__"
        read_only_fields = ["created_by", "created_at"]


class ProjectCriteriaCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = ProjectCriteria
        fields = ["nom", "poids"]
        read_only_fields = ["created_by"]

    def validate_poids(self, value):
        if value < 1 or value > 100:
            raise serializers.ValidationError("Le poids doit être compris entre 1 et 100.")
        return value

    def create(self, validated_data):
        if "projet" not in validated_data:
            validated_data["projet"] = self.context.get("projet")
        if "created_by" not in validated_data:
            request = self.context.get("request")
            if request and request.user:
                validated_data["created_by"] = request.user
        return super().create(validated_data)


class ProjectSerializer(serializers.ModelSerializer):

    chef_projet = serializers.ReadOnlyField(source="chef_projet.email")
    responsable_finance = serializers.ReadOnlyField(source="responsable_finance.email")
    organization = serializers.ReadOnlyField(source="organization.name")
    criteres = ProjectCriteriaSerializer(many=True, read_only=True)

    class Meta:
        model = Project
        fields = [
            "id",
            "name",
            "code",
            "description",
            "region",
            "objectif",
            "start_date",
            "end_date",
            "budget",
            "chef_projet",
            "responsable_finance",
            "organization",
            "created_by",
            "created_at",
            "updated_at",
            "archived",
            "criteres",
        ]
        read_only_fields = [
            "id",
            "code",
            "created_by",
            "created_at",
            "updated_at",
            "archived",
        ]


class ProjectCreateSerializer(serializers.ModelSerializer):

    chef_projet = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        write_only=True,
    )
    responsable_finance = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        write_only=True,
    )
    criteres = ProjectCriteriaCreateSerializer(many=True, write_only=True, required=False)

    class Meta:
        model = Project
        fields = [
            "name",
            "description",
            "region",
            "objectif",
            "start_date",
            "end_date",
            "chef_projet",
            "responsable_finance",
            "criteres",
            "code",
            "budget",
            "organization",
            "created_by",
        ]
        read_only_fields = [
            "code",
            "budget",
            "organization",
            "created_by",
        ]

    def validate_name(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("Le nom du projet est obligatoire.")
        return value

    def validate(self, attrs):
        start_date = attrs.get("start_date")
        end_date = attrs.get("end_date")
        if start_date and end_date and start_date > end_date:
            raise serializers.ValidationError({
                "end_date": "La date de fin doit être postérieure à la date de début."
            })

        criteres = attrs.get("criteres", [])
        total_poids = 0
        for idx, c in enumerate(criteres):
            poids = c.get("poids", 0)
            if poids < 1 or poids > 100:
                raise serializers.ValidationError({
                    "criteres": f"Le critère #{idx + 1} a un poids invalide ({poids}). Il doit être compris entre 1 et 100."
                })
            total_poids += poids

        if total_poids != 100:
            raise serializers.ValidationError({
                "criteres": f"La somme des poids des critères doit être exactement 100. Total actuel : {total_poids}."
            })
        return attrs

    def create(self, validated_data):
        request = self.context["request"]
        criteres_data = validated_data.pop("criteres", [])

        project = Project.objects.create(
            **validated_data,
            organization=request.user.organization,
            created_by=request.user,
            budget=0,
        )

        for critere_data in criteres_data:
            ProjectCriteria.objects.create(
                projet=project,
                created_by=request.user,
                **critere_data,
            )

        return project


class BudgetUpdateSerializer(serializers.ModelSerializer):

    budget = serializers.DecimalField(max_digits=12, decimal_places=2)

    class Meta:
        model = Project
        fields = ["budget"]
