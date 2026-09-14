import { ref } from "vue"
import { defineStore } from "pinia"
import { agentService } from "@/modules/agent/services/agentService.js"

export const useAgentStore = defineStore("agent", () => {
  const campagnes = ref([])
  const collectes = ref([])
  const statistiques = ref({
    campagnesTotales: 0,
    campagnesEnCours: 0,
    campagnesTerminees: 0,
    campagnesPlanifiees: 0,
    collecteTotale: 0,
    objectifTotal: 0,
    tauxRealisation: 0,
    collectesTerrain: 0,
    elementsSynchronises: 0,
    elementsEnAttente: 0,
  })
  const loading = ref(false)
  const error = ref(null)

  const formatMontant = (montant) => {
    if (!montant) return "0"
    return montant.toLocaleString("fr-FR")
  }

  const fetchAll = async () => {
    loading.value = true
    error.value = null
    try {
      campagnes.value = agentService.getCampagnes().value
      collectes.value = agentService.getCollectesTerrain().value
      statistiques.value = agentService.getStatistiques()
    } catch (e) {
      error.value = e.message || "Erreur lors du chargement des données"
    } finally {
      loading.value = false
    }
  }

  fetchAll()

  return {
    campagnes,
    collectes,
    statistiques,
    loading,
    error,
    formatMontant,
    fetchAll,
  }
})

