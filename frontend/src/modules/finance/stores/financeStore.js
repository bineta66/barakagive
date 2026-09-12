import { ref, computed } from "vue"
import { defineStore } from "pinia"
import { financeService } from "@/modules/finance/services/financeService.js"

export const useFinanceStore = defineStore("finance", () => {
  const finances = ref([])
  const projetsAssignes = ref([])
  const depensesParCategorie = ref([])
  const dernieresOperations = ref([])
  const statistiques = ref({
    budgetTotal: 0,
    depensesRealisees: 0,
    soldeDisponible: 0,
    tauxExecution: 0,
  })
  const loading = ref(false)
  const error = ref(null)

  const formatMontant = (montant) => {
    if (!montant) return "0"
    return montant.toLocaleString("fr-FR")
  }

  const tauxExecutionValue = computed(() => {
    if (statistiques.value.budgetTotal > 0) {
      return Math.round((statistiques.value.depensesRealisees / statistiques.value.budgetTotal) * 100)
    }
    return 0
  })

  const fetchAll = async () => {
    loading.value = true
    error.value = null
    try {
      finances.value = financeService.getFinances().value
      projetsAssignes.value = financeService.getProjetsAssignes().value
      depensesParCategorie.value = financeService.getDepensesParCategorie()
      dernieresOperations.value = financeService.getDernieresOperations()
      statistiques.value = financeService.getStatistiques()
    } catch (e) {
      error.value = e.message || "Erreur lors du chargement des données"
    } finally {
      loading.value = false
    }
  }

  fetchAll()

  return {
    finances,
    projetsAssignes,
    depensesParCategorie,
    dernieresOperations,
    statistiques,
    loading,
    error,
    formatMontant,
    tauxExecutionValue,
    fetchAll,
  }
})
