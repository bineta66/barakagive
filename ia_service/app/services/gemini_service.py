import os
import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold

logger = logging.getLogger(__name__)

# Configuration
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = "gemini-2.5-flash"

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
else:
    logger.warning("GEMINI_API_KEY not configured. IA service will return mock data.")


class GeminiService:
    def __init__(self):
        self.model = None
        if GEMINI_API_KEY:
            self.model = genai.GenerativeModel(
                GEMINI_MODEL,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.3,
                    top_p=0.8,
                    top_k=40,
                    max_output_tokens=4096,
                ),
                safety_settings={
                    HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                    HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                    HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                    HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                }
            )

    def _call_gemini(self, prompt: str) -> str:
        if not self.model:
            return self._mock_response(prompt)
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            logger.error(f"Gemini API error: {e}")
            return self._mock_response(prompt)

    def _mock_response(self, prompt: str) -> str:
        """Return mock response when Gemini is not configured"""
        if "executive" in prompt.lower():
            return json.dumps({
                "resume": "L'analyse des campagnes actives révèle une situation globalement stable. Deux zones nécessitent une attention particulière.",
                "alert": "ORANGE",
                "campagne_prioritaire": {
                    "id": "camp-001",
                    "nom": "Campagne Kaolack 2025",
                    "region": "Kaolack",
                    "urgence": "Élevée",
                    "beneficiaires_count": 1250,
                    "score": 87.5
                },
                "zone_prioritaire": {
                    "id": "zone-001",
                    "nom": "Kaolack Centre",
                    "region": "Kaolack",
                    "score": 92.3,
                    "beneficiaires": 450,
                    "niveau_urgence": "Très élevée"
                },
                "budget": {
                    "total": 50000000,
                    "taux": 65.2,
                    "solde": 17400000,
                    "alerte": True
                },
                "recommandations": [
                    "Prioriser la distribution dans la zone Kaolack Centre",
                    "Revoir l'allocation budgétaire pour les zones à forte urgence",
                    "Planifier une mission de terrain dans les 48h"
                ]
            })
        elif "zone" in prompt.lower() and "priorit" in prompt.lower():
            return json.dumps({
                "region": "Kaolack",
                "zones_prioritaires": [
                    {"id": "zone-001", "nom": "Kaolack Centre", "region": "Kaolack", "departement": "Kaolack", "score_total": 92.3, "beneficiaires": 450, "niveau_urgence": "Très élevée"},
                    {"id": "zone-002", "nom": "Kaolack Nord", "region": "Kaolack", "departement": "Kaolack", "score_total": 78.5, "beneficiaires": 320, "niveau_urgence": "Élevée"},
                    {"id": "zone-003", "nom": "Kaolack Sud", "region": "Kaolack", "departement": "Kaolack", "score_total": 55.2, "beneficiaires": 180, "niveau_urgence": "Moyenne"},
                    {"id": "zone-004", "nom": "Nioro", "region": "Kaolack", "departement": "Nioro", "score_total": 42.1, "beneficiaires": 120, "niveau_urgence": "Faible"},
                    {"id": "zone-005", "nom": "Guinguinéo", "region": "Kaolack", "departement": "Guinguinéo", "score_total": 38.7, "beneficiaires": 95, "niveau_urgence": "Faible"}
                ]
            })
        elif "zone_detail" in prompt.lower() or ("zone" in prompt.lower() and "detail" in prompt.lower()):
            return json.dumps({
                "id": "zone-001",
                "nom": "Kaolack Centre",
                "region": "Kaolack",
                "departement": "Kaolack",
                "niveau": "Très élevée",
                "score_total": 92.3,
                "beneficiaires": 450,
                "justification": "Cette zone concentre le plus grand nombre de bénéficiaires vulnérables avec un taux de couverture insuffisant. Les indicateurs de sécurité alimentaire sont critiques.",
                "recommandation": "Déployer immédiatement une équipe mobile pour distribution d'urgence. Coordonner avec les autorités locales pour l'accès sécurisé.",
                "top5_beneficiaires": [
                    {"nom": "Diop", "prenom": "Fatou", "score": 98.5, "vulnerabilite": "Critique"},
                    {"nom": "Sarr", "prenom": "Moussa", "score": 95.2, "vulnerabilite": "Critique"},
                    {"nom": "Ndiaye", "prenom": "Awa", "score": 93.7, "vulnerabilite": "Élevée"},
                    {"nom": "Ba", "prenom": "Oumar", "score": 91.4, "vulnerabilite": "Élevée"},
                    {"nom": "Fall", "prenom": "Khady", "score": 89.8, "vulnerabilite": "Élevée"}
                ]
            })
        elif "finance" in prompt.lower() or "budget" in prompt.lower():
            return json.dumps({
                "alert": "YELLOW",
                "resume": "Le taux d'exécution budgétaire est de 68%. Les dépenses sont concentrées sur l'alimentaire et la logistique. Solde restant suffisant jusqu'à la clôture.",
                "prediction": "À rythme constant, le budget sera épuisé 12 jours avant la date de clôture prévue. Risque de dépassement sur le poste transport.",
                "justification": "L'analyse des dépenses par zone montre que Kaolack Centre absorbe 45% du budget pour 30% des bénéficiaires. Le poste transport a augmenté de 23% vs prévision.",
                "recommandation": "Réallouer 15% du budget logistique vers l'alimentaire. Négocier les tarifs transport avec les prestataires locaux.",
                "budget": 50000000,
                "depenses": 34000000,
                "solde": 16000000,
                "taux_execution": 68.0,
                "date_cloture": "2025-12-31",
                "jours_restants": 45,
                "zone_plus_depensiere": "Kaolack Centre",
                "categorie_plus_depensiere": "Alimentaire"
            })
        return json.dumps({"error": "Unknown prompt type"})

    def analyze_executive(self, data: Dict[str, Any]) -> Dict[str, Any]:
        prompt = f"""
Tu es un expert en analyse stratégique humanitaire pour l'ONG BarakaGive360.

DONNÉES REÇUES:
{json.dumps(data, ensure_ascii=False, indent=2)}

TÂCHE: Génère un "Executive Insight" pour le Gérant de l'ONG.

RÈGLES STRICTES:
1. Utilise UNIQUEMENT les données fournies. N'invente rien.
2. Retourne UNIQUEMENT un JSON valide (pas de markdown, pas de texte).
3. Structure de réponse EXACTE:
{{
  "resume": "Résumé stratégique en 2-3 phrases max",
  "alert": "GREEN|YELLOW|ORANGE|RED",
  "campagne_prioritaire": {{"id": "...", "nom": "...", "region": "...", "urgence": "Faible|Moyenne|Élevée|Très élevée|Critique", "beneficiaires_count": 0, "score": 0.0}} ou null,
  "zone_prioritaire": {{"id": "...", "nom": "...", "region": "...", "score": 0.0, "beneficiaires": 0, "niveau_urgence": "Faible|Moyenne|Élevée|Très élevée|Critique"}} ou null,
  "budget": {{"total": 0.0, "taux": 0.0, "solde": 0.0, "alerte": false}} ou null,
  "recommandations": ["rec1", "rec2", "rec3"] (max 3)
}}

CRITÈRES D'ALERTE:
- RED: Urgence critique, vies en danger, budget épuisé
- ORANGE: Anomalies significatives nécessitant action sous 48h
- YELLOW: Points d'attention, surveillance recommandée
- GREEN: Situation normale

Si aucune donnée ou aucune urgence: alert="GREEN", resume="Aucune urgence stratégique n'est détectée actuellement.", autres champs null.
"""
        response = self._call_gemini(prompt)
        try:
            return json.loads(response)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse Gemini executive response: {e}")
            return self._mock_response("executive")

    def analyze_zones(self, data: Dict[str, Any]) -> Dict[str, Any]:
        prompt = f"""
Tu es un expert en analyse de zones humanitaires pour BarakaGive360.

DONNÉES REÇUES:
{json.dumps(data, ensure_ascii=False, indent=2)}

TÂCHE: Classe les zones par priorité d'intervention pour une région donnée.

RÈGLES STRICTES:
1. Utilise UNIQUEMENT les données fournies.
2. Retourne UNIQUEMENT un JSON valide.
3. Structure:
{{
  "region": "nom_region",
  "zones_prioritaires": [
    {{"id": "...", "nom": "...", "region": "...", "departement": "...", "score_total": 0.0, "beneficiaires": 0, "niveau_urgence": "Faible|Moyenne|Élevée|Très élevée|Critique"}}
  ]
}}

Le score_total doit refléter: vulnérabilité bénéficiaires (40%), densité population (20%), accès/insécurité (20%), ressources disponibles (20%).
Trie par score décroissant.
"""
        response = self._call_gemini(prompt)
        try:
            return json.loads(response)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse Gemini zones response: {e}")
            return self._mock_response("zone")

    def analyze_zone_detail(self, data: Dict[str, Any], zone_id: str) -> Dict[str, Any]:
        prompt = f"""
Tu es un expert en analyse de zone humanitaire pour BarakaGive360.

DONNÉES REÇUES:
{json.dumps(data, ensure_ascii=False, indent=2)}

ZONE CIBLE: {zone_id}

TÂCHE: Analyse détaillée de cette zone spécifique.

RÈGLES STRICTES:
1. Utilise UNIQUEMENT les données fournies.
2. Retourne UNIQUEMENT un JSON valide.
3. Structure:
{{
  "id": "...",
  "nom": "...",
  "region": "...",
  "departement": "...",
  "niveau": "Faible|Moyenne|Élevée|Très élevée|Critique",
  "score_total": 0.0,
  "beneficiaires": 0,
  "justification": "Explication factuelle basée sur les données",
  "recommandation": "Action concrète recommandée",
  "top5_beneficiaires": [
    {{"nom": "...", "prenom": "...", "score": 0.0, "vulnerabilite": "Faible|Moyenne|Élevée|Critique"}}
  ]
}}

Si zone non trouvée: retourner {{"message": "Zone non trouvée"}}
"""
        response = self._call_gemini(prompt)
        try:
            return json.loads(response)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse Gemini zone detail response: {e}")
            return self._mock_response("zone_detail")

    def analyze_finance(self, data: Dict[str, Any]) -> Dict[str, Any]:
        prompt = f"""
Tu es un expert financier humanitaire pour BarakaGive360.

DONNÉES REÇUES:
{json.dumps(data, ensure_ascii=False, indent=2)}

TÂCHE: Analyse budgétaire et prévision financière.

RÈGLES STRICTES:
1. Utilise UNIQUEMENT les données fournies.
2. Retourne UNIQUEMENT un JSON valide.
3. Structure:
{{
  "alert": "GREEN|YELLOW|ORANGE|RED",
  "resume": "Résumé en 2 phrases max",
  "prediction": "Prévision jusqu'à la clôture (jours restants, risque dépassement)",
  "justification": "Explication factuelle basée sur les chiffres",
  "recommandation": "Action concrète",
  "budget": 0.0,
  "depenses": 0.0,
  "solde": 0.0,
  "taux_execution": 0.0,
  "date_cloture": "YYYY-MM-DD",
  "jours_restants": 0,
  "zone_plus_depensiere": "...",
  "categorie_plus_depensiere": "..."
}}

CRITÈRES ALERTE FINANCE:
- RED: Taux > 95% OU solde < 5% budget OU jours_restants < 7
- ORANGE: Taux > 80% OU solde < 15% budget OU jours_restants < 15
- YELLOW: Taux > 65% OU solde < 30% budget
- GREEN: Autre
"""
        response = self._call_gemini(prompt)
        try:
            return json.loads(response)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse Gemini finance response: {e}")
            return self._mock_response("finance")


gemini_service = GeminiService()