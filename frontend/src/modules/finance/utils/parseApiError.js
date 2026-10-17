/**
 * Parse une erreur Axios (DRF) en message lisible.
 * DRF retourne les erreurs sous différentes formes :
 *   { "montant": ["Le montant doit être supérieur à 0."] }
 *   { "non_field_errors": ["..."] }
 *   { "detail": "..." }
 *   ou un string simple
 */
export function parseApiError(err) {
  const data = err?.response?.data

  if (!data) {
    return err?.message || "Erreur réseau ou serveur indisponible."
  }

  if (typeof data === "string") return data

  if (typeof data === "object") {
    const lines = []

    for (const [key, val] of Object.entries(data)) {
      const msgs = Array.isArray(val) ? val : [val]
      msgs.forEach((m) => {
        if (key === "non_field_errors" || key === "detail") {
          lines.push(String(m))
        } else {
          // Traduit les noms de champ vers des labels lisibles
          const label = FIELD_LABELS[key] || key
          lines.push(`${label} : ${m}`)
        }
      })
    }

    return lines.join("\n") || "Erreur de validation."
  }

  return "Erreur inconnue."
}

// Labels lisibles pour les champs backend
const FIELD_LABELS = {
  projet:             "Projet",
  montant:            "Montant",
  source_financement: "Source de financement",
  date:               "Date",
  observation:        "Observation",
  statut:             "Statut",
  bailleur:           "Bailleur",
  budget:             "Budget",
  campagne:           "Campagne",
  moyen_paiement:     "Moyen de paiement",
  region:             "Région",
  categorie:          "Catégorie",
  fournisseur:        "Fournisseur",
  description:        "Description",
  fichier:            "Fichier",
  type_fichier:       "Type de fichier",
}
