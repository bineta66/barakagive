# BarakaGive360 IA

Microservice FastAPI dédié à l'intelligence artificielle pour BarakaGive360.

## Démarrage

```bash
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## Variables d'environnement

| Variable | Description |
|---|---|
| `GEMINI_API_KEY` | Clé API Google Generative AI |
| `MODEL_NAME` | Modèle Gemini (défaut: `gemini-2.5-flash`) |

## Endpoints

| Méthode | Endpoint | Description |
|---|---|---|
| GET | `/health` | Vérification du service |
| POST | `/api/ia/priorisation` | Analyse humanitaire dynamique |
| POST | `/api/ia/budget` | Analyse intelligente du budget |

## Sécurité

- Aucune base de données.
- Aucune importation de modèle Django.
- Aucune connexion PostgreSQL.
- Communication exclusivement par JSON avec le backend Django.
- Service totalement stateless.
