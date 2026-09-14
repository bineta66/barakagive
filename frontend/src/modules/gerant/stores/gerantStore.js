import { ref, computed } from "vue"
import { defineStore } from "pinia"
import { gerantService } from "@/modules/gerant/services/gerantService.js"

export const useGerantStore = defineStore("gerant", () => {
  const projets = ref([])
  const chefsProjet = ref([])
  const responsablesFinance = ref([])
  const utilisateurs = ref([])
  const bailleurs = ref([])
  const partenaires = ref([])
  const statistiques = ref({
    totalProjets: 0,
    totalUtilisateurs: 0,
    budgetTotal: 0,
    bailleursCount: 0,
    partenairesCount: 0,
    budgetEngage: 0,
    soldeDisponible: 0,
    tauxExecution: 0,
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
      projets.value = gerantService.getProjets().value
      chefsProjet.value = gerantService.getChefsProjet().value
      responsablesFinance.value = gerantService.getResponsablesFinance().value
      utilisateurs.value = gerantService.getUtilisateurs().value
      bailleurs.value = gerantService.getBailleurs()
      partenaires.value = gerantService.getPartenaires()
      statistiques.value = gerantService.getStatistiques()
    } catch (e) {
      error.value = e.message || "Erreur lors du chargement des données"
    } finally {
      loading.value = false
    }
  }

  fetchAll()

  return {
    projets,
    chefsProjet,
    responsablesFinance,
    utilisateurs,
    bailleurs,
    partenaires,
    statistiques,
    loading,
    error,
    formatMontant,
    fetchAll,
  }
})

