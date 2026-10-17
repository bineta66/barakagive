import re
from decimal import Decimal, InvalidOperation

from rest_framework import serializers

from .models import Beneficiary, FormResponse, HumanitarianAction


class FormResponseCreateSerializer(serializers.Serializer):
    """Sérialiseur pour la création d'une réponse (format simplifié pour le frontend)."""

    question_id = serializers.UUIDField()
    value = serializers.JSONField(help_text="Valeur brute, le backend la répartit selon le type de question")

    def to_internal_value(self, data):
        if isinstance(data, dict):
            unexpected = set(data) - set(self.fields)
            if unexpected:
                raise serializers.ValidationError({
                    field: "Champ inattendu." for field in sorted(unexpected)
                })
        return super().to_internal_value(data)


class FormResponseSerializer(serializers.ModelSerializer):
    """Sérialiseur pour la lecture d'une réponse."""

    question = serializers.SerializerMethodField()

    class Meta:
        model = FormResponse
        fields = [
            "id",
            "question",
            "value_text",
            "value_number",
            "value_boolean",
            "value_date",
            "value_json",
            "created_at",
        ]

    def get_question(self, obj):
        return {
            "id": obj.question.id,
            "label": obj.question.label,
            "type": obj.question.type,
        }


class BeneficiaryCreateSerializer(serializers.Serializer):
    """Sérialiseur pour la création d'un bénéficiaire avec ses réponses (un seul JSON)."""

    campagne_id = serializers.UUIDField()
    formulaire_id = serializers.UUIDField(required=False, allow_null=True)
    zone_id = serializers.UUIDField()
    local_id = serializers.UUIDField(required=False, allow_null=True)
    device_id = serializers.CharField(max_length=100, required=False, allow_blank=True, default="web")

    beneficiary = serializers.DictField(
        help_text="Informations personnelles du bénéficiaire"
    )

    responses = FormResponseCreateSerializer(many=True, required=False, default=list)

    # Legacy/mobile clients may still send these server-owned references. They
    # are deliberately ignored; ownership is always derived from the request
    # user and the validated campaign/zone relations.
    IGNORED_SERVER_OWNED_FIELDS = {
        "organization_id", "project_id", "campaign_id", "beneficiary_id",
        "user_id", "agent_id", "campagne_nom", "zone_nom", "timestamp",
    }

    def validate(self, attrs):
        if isinstance(self.initial_data, dict):
            allowed = set(self.fields) | self.IGNORED_SERVER_OWNED_FIELDS
            unexpected = set(self.initial_data) - allowed
            if unexpected:
                raise serializers.ValidationError({
                    field: "Champ inattendu." for field in sorted(unexpected)
                })
            raw_device_id = self.initial_data.get("device_id")
            if raw_device_id is not None and not isinstance(raw_device_id, str):
                raise serializers.ValidationError({
                    "device_id": "Ce champ doit être une chaîne de caractères."
                })
        return attrs

    def validate_beneficiary(self, value):
        allowed_fields = {
            "nom", "prenom", "telephone", "sexe", "date_naissance",
            "latitude", "longitude",
        }
        unexpected = set(value) - allowed_fields
        if unexpected:
            raise serializers.ValidationError({
                field: "Champ inattendu." for field in sorted(unexpected)
            })

        required_fields = ["nom", "prenom", "telephone", "sexe", "date_naissance"]
        for field in required_fields:
            if field not in value or value[field] is None or (
                isinstance(value[field], str) and not value[field].strip()
            ):
                raise serializers.ValidationError(f"Le champ '{field}' est obligatoire.")

        for field in ("nom", "prenom", "telephone", "date_naissance"):
            if not isinstance(value[field], str):
                raise serializers.ValidationError({field: "Ce champ doit être une chaîne de caractères."})

        sexe = value.get("sexe")
        choix_valides = [c[0] for c in Beneficiary.Sexe.choices]
        if sexe not in choix_valides:
            raise serializers.ValidationError(f"Le sexe doit être parmi {choix_valides}.")

        # Les coordonnées sont facultatives, mais doivent être fournies par paire
        # et rester dans les limites géographiques même si l'API est appelée directement.
        coordinates = {}
        for field, minimum, maximum in (
            ("latitude", Decimal("-90"), Decimal("90")),
            ("longitude", Decimal("-180"), Decimal("180")),
        ):
            raw = value.get(field)
            if raw is None or (isinstance(raw, str) and not raw.strip()):
                coordinates[field] = None
                continue
            try:
                number = Decimal(str(raw))
                if not number.is_finite() or number < minimum or number > maximum:
                    raise InvalidOperation
            except (InvalidOperation, TypeError, ValueError):
                raise serializers.ValidationError({field: f"{field} doit être compris entre {minimum} et {maximum}."})
            coordinates[field] = str(number)
        if (coordinates["latitude"] is None) != (coordinates["longitude"] is None):
            raise serializers.ValidationError("La latitude et la longitude doivent être fournies ensemble.")
        value.update(coordinates)

        # Validation nom & prénom
        from apps.common.validators import validate_phone_senegal, validate_nom
        try:
            nom = validate_nom(value["nom"])
        except Exception as exc:
            raise serializers.ValidationError({"nom": str(exc)})

        try:
            prenom = validate_nom(value["prenom"])
        except Exception as exc:
            raise serializers.ValidationError({"prenom": str(exc)})

        # Validation téléphone
        try:
            validate_phone_senegal(value["telephone"])
        except Exception as e:
            raise serializers.ValidationError(str(e))

        # Validation date de naissance
        from datetime import date
        try:
            dob = value["date_naissance"]
            if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", dob):
                raise ValueError("format")
            d = date.fromisoformat(dob)
            if d >= date.today():
                raise serializers.ValidationError(
                    "La date de naissance doit être dans le passé."
                )
        except ValueError:
            raise serializers.ValidationError("La date de naissance est invalide (format attendu : YYYY-MM-DD).")

        return value

    def validate_responses(self, value):
        q_ids = [str(r.get("question_id")) for r in value if r.get("question_id")]
        if len(q_ids) != len(set(q_ids)):
            raise serializers.ValidationError("Vous ne pouvez pas envoyer plusieurs réponses pour la même question.")
        return value


class BeneficiaryUpdateSerializer(serializers.Serializer):
    """Sérialiseur pour la mise à jour des informations personnelles."""

    nom = serializers.CharField(max_length=100, required=False)
    prenom = serializers.CharField(max_length=100, required=False)
    telephone = serializers.CharField(max_length=20, required=False)
    sexe = serializers.ChoiceField(choices=Beneficiary.Sexe.choices, required=False)
    date_naissance = serializers.DateField(required=False)
    latitude = serializers.DecimalField(
        max_digits=10, decimal_places=7, min_value=Decimal("-90"),
        max_value=Decimal("90"), required=False,
    )
    longitude = serializers.DecimalField(
        max_digits=10, decimal_places=7, min_value=Decimal("-180"),
        max_value=Decimal("180"), required=False,
    )

    def validate_nom(self, value):
        from apps.common.validators import validate_nom
        try:
            return validate_nom(value)
        except Exception as exc:
            raise serializers.ValidationError(str(exc))

    def validate_prenom(self, value):
        from apps.common.validators import validate_nom
        try:
            return validate_nom(value)
        except Exception as exc:
            raise serializers.ValidationError(str(exc))

    def validate_telephone(self, value):
        from apps.common.validators import validate_phone_senegal
        try:
            return validate_phone_senegal(value)
        except Exception as exc:
            raise serializers.ValidationError(str(exc))

    def validate_date_naissance(self, value):
        from datetime import date
        if value >= date.today():
            raise serializers.ValidationError("La date de naissance doit être dans le passé.")
        return value


class BeneficiaryListSerializer(serializers.ModelSerializer):
    """Sérialiseur pour la liste des bénéficiaires, incluant les réponses détaillées."""

    campagne = serializers.SerializerMethodField()
    zone = serializers.SerializerMethodField()
    created_by = serializers.SerializerMethodField()
    responses = FormResponseSerializer(many=True, read_only=True)

    class Meta:
        model = Beneficiary
        fields = [
            "id",
            "nom",
            "prenom",
            "telephone",
            "sexe",
            "date_naissance",
            "campagne",
            "zone",
            "score_vulnerabilite",
            "sync_status",
            "created_by",
            "created_at",
            "responses",
        ]

    def get_campagne(self, obj):
        return {
            "id": obj.campagne.id,
            "code_campagne": obj.campagne.code_campagne,
            "nom": obj.campagne.nom,
        }

    def get_zone(self, obj):
        return {
            "id": obj.zone.id,
            "nom": obj.zone.nom,
        }

    def get_created_by(self, obj):
        return {
            "id": obj.created_by.id,
            "email": obj.created_by.email,
            "full_name": obj.created_by.full_name,
        }


class BeneficiaryDetailSerializer(serializers.ModelSerializer):
    """Sérialiseur pour le détail d'un bénéficiaire avec ses réponses."""

    campagne = serializers.SerializerMethodField()
    zone = serializers.SerializerMethodField()
    formulaire = serializers.SerializerMethodField()
    responses = FormResponseSerializer(many=True, read_only=True)
    created_by = serializers.SerializerMethodField()

    class Meta:
        model = Beneficiary
        fields = [
            "id",
            "nom",
            "prenom",
            "telephone",
            "sexe",
            "date_naissance",
            "latitude",
            "longitude",
            "local_id",
            "device_id",
            "campagne",
            "zone",
            "formulaire",
            "score_vulnerabilite",
            "sync_status",
            "responses",
            "created_by",
            "created_at",
            "updated_at",
        ]

    def get_campagne(self, obj):
        return {
            "id": obj.campagne.id,
            "code_campagne": obj.campagne.code_campagne,
            "nom": obj.campagne.nom,
            "projet": {
                "id": obj.campagne.projet.id,
                "code": obj.campagne.projet.code,
                "name": obj.campagne.projet.name,
            },
        }

    def get_zone(self, obj):
        return {
            "id": obj.zone.id,
            "nom": obj.zone.nom,
            "region": obj.zone.region.nom,
            "departement": obj.zone.departement.nom,
        }

    def get_formulaire(self, obj):
        if hasattr(obj, '_formulaire_id'):
            return {"id": obj._formulaire_id}
        # Récupérer le formulaire via les réponses
        if obj.responses.exists():
            return {"id": obj.responses.first().formulaire.id}
        return None

    def get_created_by(self, obj):
        return {
            "id": obj.created_by.id,
            "email": obj.created_by.email,
            "full_name": obj.created_by.full_name,
            "role": obj.created_by.role,
        }


class BeneficiarySyncSerializer(serializers.Serializer):
    """Sérialiseur pour la réponse de synchronisation."""

    synced = serializers.IntegerField()
    duplicates = serializers.IntegerField()
    failed = serializers.IntegerField()
    details = serializers.ListField(child=serializers.DictField(), required=False)


class HumanitarianActionSerializer(serializers.ModelSerializer):
    beneficiary = serializers.UUIDField(source="beneficiary_id", read_only=True)
    campagne = serializers.UUIDField(source="campagne_id", read_only=True)
    agent = serializers.SerializerMethodField()

    class Meta:
        model = HumanitarianAction
        fields = [
            "id", "beneficiary", "campagne", "agent", "type_aide",
            "date_action", "quantite", "statut", "resultat", "created_at",
        ]
        read_only_fields = ["id", "beneficiary", "campagne", "agent", "created_at"]

    def get_agent(self, obj):
        return {
            "id": obj.agent_id,
            "full_name": obj.agent.full_name,
            "email": obj.agent.email,
        }

    def validate_quantite(self, value):
        if value <= 0:
            raise serializers.ValidationError("La quantité doit être supérieure à zéro.")
        return value

    def validate(self, attrs):
        beneficiary = self.context.get("beneficiary")
        request = self.context.get("request")
        if beneficiary is None or request is None:
            raise serializers.ValidationError("Le bénéficiaire et l'utilisateur authentifié sont requis.")
        campaign = beneficiary.campagne
        if (
            beneficiary.organization_id != campaign.organization_id
            or beneficiary.zone.organization_id != beneficiary.organization_id
            or campaign.projet.organization_id != campaign.organization_id
            or request.user.organization_id != beneficiary.organization_id
        ):
            raise serializers.ValidationError("Le bénéficiaire, sa campagne, sa zone et votre compte doivent appartenir à la même ONG.")
        return attrs

    def create(self, validated_data):
        beneficiary = self.context["beneficiary"]
        request = self.context["request"]
        from apps.campaigns.models import CampagneAffectation

        assigned = CampagneAffectation.objects.filter(
            campagne=beneficiary.campagne,
            agent=request.user,
        ).filter(zone__in=[beneficiary.zone.nom, str(beneficiary.zone_id)]).exists()
        if not assigned:
            raise serializers.ValidationError(
                "Vous devez être affecté à la campagne et à la zone du bénéficiaire."
            )

        return HumanitarianAction.objects.create(
            beneficiary=beneficiary,
            campagne=beneficiary.campagne,
            agent=request.user,
            **validated_data,
        )
