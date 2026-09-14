import { ref, computed } from "vue"
import { defineStore } from "pinia"
import { financeService } from "@/modules/finance/services/financeService.js"

export const useFinanceStore = defineStore("finance", () => {
  const finances = ref([])
  const projetsAssignes = ref([])
  const depensesParCategorie = ref([])
  const dernieresOperations = ref([])
  const budgets = ref([])
  const budgetsStatistiques = ref({
    budgetTotal: 0,
    budgetConsomme: 0,
    soldeDisponible: 0,
    projetsBudgétises: 0,
  })
  const donsFinancements = ref([])
  const donsStatistiques = ref({
    totalFinancements: 0,
    nombreBailleurs: 0,
    financementDuMois: 0,
    projetsFinances: 0,
  })
  const depenses = ref([])
  const depensesStatistiques = ref({
    depensesTotales: 0,
    depensesDuMois: 0,
    nombreOperations: 0,
    budgetRestant: 0,
  })
  const justificatifs = ref([])
  const justificatifsStatistiques = ref({
    valides: 0,
    enAttente: 0,
    montantJustifie: 0,
    depensesSansJustificatif: 0,
  })
  const categoriesDepense = ref([])
  const modesPaiement = ref([])
  const typesDocument = ref([])
  const bailleurs = ref([])
  const typesFinancement = ref([])
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
      budgets.value = financeService.getAllBudgets().value
      budgetsStatistiques.value = financeService.getBudgetsStatistiques()
      donsFinancements.value = financeService.getAllDonsFinancements().value
      donsStatistiques.value = financeService.getDonsStatistiques()
      depenses.value = financeService.getAllDepenses().value
      depensesStatistiques.value = financeService.getDepensesStatistiques()
      justificatifs.value = financeService.getAllJustificatifs().value
      justificatifsStatistiques.value = financeService.getJustificatifsStatistiques()
      categoriesDepense.value = financeService.getCategoriesDepense()
      modesPaiement.value = financeService.getModesPaiement()
      typesDocument.value = financeService.getTypesDocument()
      bailleurs.value = financeService.getBailleurs()
      typesFinancement.value = financeService.getTypesFinancement()
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
    budgets,
    budgetsStatistiques,
    donsFinancements,
    donsStatistiques,
    depenses,
    depensesStatistiques,
    justificatifs,
    justificatifsStatistiques,
    categoriesDepense,
    modesPaiement,
    typesDocument,
    bailleurs,
    typesFinancement,
    statistiques,
    loading,
    error,
    formatMontant,
    tauxExecutionValue,
    fetchAll,
  }
})
