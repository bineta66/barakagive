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

    def _score_to_urgence(self, score: float) -> str:
        """Convert numeric score to urgency level."""
        if score >= 80:
            return "Très élevée"
        elif score >= 60:
            return "Élevée"
        elif score >= 40:
            return "Moyenne"
        elif score >= 20:
            return "Faible"
        return "Faible"

    def _call_gemini(self, prompt: str) -> str:
        if not self.model:
            return self._mock_response(prompt, {})
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            logger.error(f"Gemini API error: {e}")
            return self._mock_response(prompt, {})

    def _mock_response(self, prompt: str, data: Dict[str, Any] = None, zone_id: str = None) -> str:
        """Return mock response when Gemini is not configured"""
        if data is None:
            data = {}
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
            # Extract zones from payload data
            zones_from_data = data.get("zones", [])
            if not zones_from_data:
                zones_from_data = data.get("zones_data", [])
            
            zones_prioritaires = []
            for i, zone in enumerate(zones_from_data):
                zones_prioritaires.append({
                    "id": str(zone.get("id", f"zone-{i+1}")),
                    "nom": zone.get("nom", f"Zone {i+1}"),
                    "region": zone.get("region", ""),
                    "departement": zone.get("departement", zone.get("region", "")),
                    "score_total": float(zone.get("score_moyen", zone.get("score_total", 50.0))),
                    "beneficiaires": int(zone.get("beneficiaires", 0)),
                    "niveau_urgence": self._score_to_urgence(zone.get("score_moyen", zone.get("score_total", 50.0)))
                })
            
            # Sort by score descending
            zones_prioritaires.sort(key=lambda x: x["score_total"], reverse=True)
            
            region = zones_from_data[0].get("region", "") if zones_from_data else ""
            return json.dumps({
                "region": region,
                "zones_prioritaires": zones_prioritaires
            })
        elif "zone_detail" in prompt.lower() or ("zone" in prompt.lower() and "detail" in prompt.lower()):
            # Find the specific zone from payload
            zones_from_data = data.get("zones", [])
            if not zones_from_data:
                zones_from_data = data.get("zones_data", [])
            
            target_zone = None
            for zone in zones_from_data:
                if str(zone.get("id", "")) == str(zone_id) or zone.get("nom") == zone_id:
                    target_zone = zone
                    break
            
            if not target_zone and zones_from_data:
                target_zone = zones_from_data[0]
            
            if not target_zone:
                return json.dumps({"message": "Zone non trouvée"})
            
            score = float(target_zone.get("score_moyen", target_zone.get("score_total", 50.0)))
            beneficiaires = int(target_zone.get("beneficiaires", 0))
            
            # Generate mock top 5 based on zone data
            top5 = []
            for i in range(min(5, beneficiaires)):
                top5.append({
                    "nom": f"Bénéficiaire {i+1}",
                    "prenom": "",
                    "score": max(50, score - i * 3),
                    "vulnerabilite": self._score_to_urgence(max(50, score - i * 3))
                })
            
            return json.dumps({
                "id": str(target_zone.get("id", zone_id)),
                "nom": target_zone.get("nom", "Zone"),
                "region": target_zone.get("region", ""),
                "departement": target_zone.get("departement", target_zone.get("region", "")),
                "niveau": self._score_to_urgence(score),
                "score_total": score,
                "beneficiaires": beneficiaires,
                "justification": f"Analyse basée sur {beneficiaires} bénéficiaires avec score moyen {score:.1f}.",
                "recommandation": "Adapter les interventions selon le niveau de vulnérabilité identifié.",
                "top5_beneficiaires": top5
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
            return self._mock_response("executive", data)

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
            return self._mock_response("zone", data)

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
            return self._mock_response("zone_detail", data, zone_id)

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
            return self._mock_response("finance", data)

    def analyze_region(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyse d'une région par l'IA (Gemini).
        Reçoit les zones avec scores calculés par Django et retourne une analyse humaine.
        """
        prompt = f"""
Tu es un expert en analyse humanitaire pour BarakaGive.
Tu rédiges l'analyse pour le Chef de Projet.

DONNÉES REÇUES (scores calculés par Django, NE JAMAIS recalculer):
{json.dumps(data, ensure_ascii=False, indent=2)}

TÂCHE: Génère une analyse humaine et des recommandations pour cette région.

RÈGLES STRICTES:
1. Utilise UNIQUEMENT les données fournies. N'invente aucun chiffre.
2. NE RECALCULE JAMAIS les scores - ils viennent de Django.
3. Retourne UNIQUEMENT un JSON valide (pas de markdown, pas de texte explicatif).
4. Structure de réponse EXACTE:
{{
  "executive_summary": "La région de {{region}} compte {{total_beneficiaries}} bénéficiaires répartis dans {{zones_count}} zones. {{zone_max}} présente le niveau de vulnérabilité le plus élevé avec un score moyen de {{score_max}}/100.",
  "zone_analysis": [
    {{"zone": "{{nom_zone_1}}", "summary": "Analyse factuelle de cette zone basée sur son score et son nombre de bénéficiaires."}},
    {{"zone": "{{nom_zone_2}}", "summary": "Analyse factuelle de cette zone basée sur son score et son nombre de bénéficiaires."}}
  ],
  "recommendations": [
    "Action concrète prioritaire pour la zone la plus vulnérable.",
    "Action pour la zone suivante.",
    "Action de suivi pour les zones moins critiques."
  ],
  "generated_at": "2026-09-18T12:00:00Z"
}}

CONSIGNES DE RÉDACTION:
- executive_summary: 2-3 phrases max, factuel, cite les chiffres clés.
- zone_analysis: Une entrée par zone fournie, dans l'ordre reçu (déjà triées par score décroissant).
  Le summary doit expliquer POURQUOI cette zone a ce niveau (score + nb bénéficiaires).
- recommendations: 3 actions concrètes, ordonnées par priorité.
- generated_at: Date ISO 8601 UTC (sera ajoutée automatiquement si manquante).

NIVEAUX DE VULNÉRABILITÉ (pour référence, ne pas recalculer):
- TRES_ELEVEE (score >= 80): Vulnérabilité critique, intervention urgente
- ELEVEE (score 60-79): Vulnérabilité forte, intervention prioritaire
- MOYENNE (score 40-59): Vulnérabilité modérée, suivi rapproché
- FAIBLE (score 20-39): Vulnérabilité limitée, surveillance
- AUCUNE_DONNEE (score 0, 0 bénéficiaires): Pas de données collectées

EXEMPLE:
Si zones = [
  {{"name": "Kaolack Centre", "score": 88, "beneficiaries": 32, "level": "TRES_ELEVEE"}},
  {{"name": "Medina", "score": 66, "beneficiaries": 21, "level": "ELEVEE"}},
  {{"name": "Ndorong", "score": 38, "beneficiaries": 12, "level": "FAIBLE"}}
]
Alors executive_summary = "La région de Kaolack compte 65 bénéficiaires répartis dans 3 zones. Kaolack Centre présente le niveau de vulnérabilité le plus élevé avec un score moyen de 88/100."
"""
        if not self.model:
            return self._mock_region_response(data)

        response = self._call_gemini(prompt)
        try:
            result = json.loads(response)
            # Ensure required fields exist
            if not isinstance(result, dict) or "executive_summary" not in result or "zone_analysis" not in result:
                return self._mock_region_response(data)
            # Ensure generated_at is present
            if "generated_at" not in result:
                result["generated_at"] = datetime.utcnow().isoformat() + "Z"
            return result
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse Gemini region response: {e}")
            return self._mock_region_response(data)

    def _mock_region_response(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Mock response for region analysis when Gemini is not configured"""
        zones = data.get("zones", [])
        region = data.get("region", "Inconnue")
        campaign = data.get("campaign", "Campagne")
        total_beneficiaries = data.get("total_beneficiaries", 0)
        zones_count = data.get("zones_count", len(zones))
        
        if zones:
            zone_max = zones[0]["name"]
            score_max = zones[0]["score"]
        else:
            zone_max = "Aucune"
            score_max = 0
        
        executive_summary = (
            f"La région de {region} compte {total_beneficiaries} bénéficiaires "
            f"répartis dans {zones_count} zones. "
            f"{zone_max} présente le niveau de vulnérabilité le plus élevé avec un score moyen de {score_max}/100."
        )
        
        zone_analysis = []
        for zone in zones:
            level = zone.get("level", "FAIBLE")
            if level == "TRES_ELEVEE":
                summary = f"Cette zone est prioritaire en raison du nombre important de ménages très vulnérables (score: {zone['score']}/100, {zone['beneficiaries']} bénéficiaires)."
            elif level == "ELEVEE":
                summary = f"La situation reste préoccupante mais moins critique que les zones prioritaires (score: {zone['score']}/100, {zone['beneficiaries']} bénéficiaires)."
            elif level == "AUCUNE_DONNEE":
                summary = "Aucune donnée collectée dans cette zone pour le moment."
            else:
                summary = f"La vulnérabilité est {level.lower()} et les besoins immédiats sont limités (score: {zone['score']}/100, {zone['beneficiaries']} bénéficiaires)."
            zone_analysis.append({"zone": zone["name"], "summary": summary})
        
        recommendations = []
        for i, zone in enumerate(zones):
            if i == 0:
                recommendations.append(f"Déployer l'équipe en priorité à {zone['name']}.")
            elif i == 1:
                recommendations.append(f"Prévoir une deuxième intervention à {zone['name']}.")
            else:
                recommendations.append(f"Maintenir un suivi régulier à {zone['name']}.")
        
        return {
            "executive_summary": executive_summary,
            "zone_analysis": zone_analysis,
            "recommendations": recommendations,
            "generated_at": datetime.utcnow().isoformat() + "Z"
        }


gemini_service = GeminiService()