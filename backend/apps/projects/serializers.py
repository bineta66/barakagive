from rest_framework import serializers

from apps.accounts.models import User
from .models import Project, ProjectCriteria


class ProjectCriteriaSerializer(serializers.ModelSerializer):

    class Meta:
        model = ProjectCriteria
        fields = "__all__"
        read_only_fields = ["created_by", "created_at"]


class ProjectSerializer(serializers.ModelSerializer):

    chef_projet = serializers.ReadOnlyField(source="chef_projet.email")
    responsable_finance = serializers.ReadOnlyField(source="responsable_finance.email")
    organization = serializers.ReadOnlyField(source="organization.name")

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
    criteria_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=ProjectCriteria.objects.all(),
        write_only=True,
        required=False,
        default=[],
    )

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
            "criteria_ids",
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
        return attrs

    def create(self, validated_data):
        request = self.context["request"]
        criteria_ids = validated_data.pop("criteria_ids", [])

        project = Project.objects.create(
            **validated_data,
            organization=request.user.organization,
            created_by=request.user,
            budget=0,
        )

        if criteria_ids:
            project.criteria.set(criteria_ids)

        return project


class BudgetUpdateSerializer(serializers.ModelSerializer):

    budget = serializers.DecimalField(max_digits=12, decimal_places=2)

    class Meta:
        model = Project
        fields = ["budget"]
