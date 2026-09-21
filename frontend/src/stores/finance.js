import { ref, computed } from "vue"
import { defineStore } from "pinia"
import financeApi from "@/services/financeApi.js"

export const useFinanceStore = defineStore("finance", () => {
  // State directly hydrated from Django REST API (no custom client-side financial math)
  const dashboardData = ref({
    budget_total: 0,
    dons_recus: 0,
    depenses_totales: 0,
    solde: 0,
    taux_execution: 0,
  })

  const budgets = ref([])
  const dons = ref([])
  const depenses = ref([])
  const justifications = ref([])
  const aiAnalysis = ref(null)
  const reportData = ref(null)
  const filtersData = ref({
    projets: [],
    campagnes: [],
    regions: [],
  })

  const loading = ref(false)
  const error = ref(null)

  // Actions
  const fetchDashboard = async () => {
    loading.value = true
    error.value = null
    try {
      const res = await financeApi.getDashboard()
      dashboardData.value = res.data
    } catch (err) {
      error.value = err.response?.data?.detail || "Erreur lors du chargement du tableau de bord"
    } finally {
      loading.value = false
    }
  }

  const fetchBudgets = async (params = {}) => {
    loading.value = true
    error.value = null
    try {
      const res = await financeApi.getBudgets(params)
      budgets.value = Array.isArray(res.data) ? res.data : res.data.results || []
    } catch (err) {
      error.value = err.response?.data?.detail || "Erreur lors du chargement des budgets"
    } finally {
      loading.value = false
    }
  }

  const addBudget = async (payload) => {
    loading.value = true
    error.value = null
    try {
      await financeApi.createBudget(payload)
      await fetchBudgets()
      await fetchDashboard()
    } catch (err) {
      error.value = err.response?.data || "Erreur lors de la création du budget"
      throw err
    } finally {
      loading.value = false
    }
  }

  const updateBudget = async (id, payload) => {
    loading.value = true
    error.value = null
    try {
      await financeApi.updateBudget(id, payload)
      await fetchBudgets()
      await fetchDashboard()
    } catch (err) {
      error.value = err.response?.data || "Erreur lors de la modification du budget"
      throw err
    } finally {
      loading.value = false
    }
  }

  const cloturerBudget = async (id) => {
    loading.value = true
    error.value = null
    try {
      await financeApi.cloturerBudget(id)
      await fetchBudgets()
      await fetchDashboard()
    } catch (err) {
      error.value = err.response?.data || "Erreur lors de la clôture du budget"
      throw err
    } finally {
      loading.value = false
    }
  }

  const fetchDonations = async (params = {}) => {
    loading.value = true
    error.value = null
    try {
      const res = await financeApi.getDonations(params)
      dons.value = Array.isArray(res.data) ? res.data : res.data.results || []
    } catch (err) {
      error.value = err.response?.data?.detail || "Erreur lors du chargement des dons"
    } finally {
      loading.value = false
    }
  }

  const addDonation = async (payload) => {
    loading.value = true
    error.value = null
    try {
      await financeApi.createDonation(payload)
      await fetchDonations()
      await fetchDashboard()
    } catch (err) {
      error.value = err.response?.data || "Erreur lors de l'ajout du don"
      throw err
    } finally {
      loading.value = false
    }
  }

  const fetchExpenses = async (params = {}) => {
    loading.value = true
    error.value = null
    try {
      const res = await financeApi.getExpenses(params)
      const list = Array.isArray(res.data) ? res.data : res.data.results || []
      depenses.value = list
      return list
    } catch (err) {
      error.value = err.response?.data?.detail || "Erreur lors du chargement des dépenses"
    } finally {
      loading.value = false
    }
  }

  const addExpense = async (payload) => {
    loading.value = true
    error.value = null
    try {
      await financeApi.createExpense(payload)
      await fetchExpenses()
      await fetchDashboard()
    } catch (err) {
      error.value = err.response?.data || "Erreur lors de la création de la dépense"
      throw err
    } finally {
      loading.value = false
    }
  }

  const updateExpenseStatus = async (id, statut) => {
    loading.value = true
    error.value = null
    try {
      await financeApi.updateExpenseStatus(id, statut)
      await fetchExpenses()
      await fetchDashboard()
    } catch (err) {
      error.value = err.response?.data || "Erreur lors de la mise à jour du statut"
      throw err
    } finally {
      loading.value = false
    }
  }

  const fetchAllJustifications = async () => {
    loading.value = true
    error.value = null
    try {
      const expList = await fetchExpenses()
      const justPromises = expList.map(async (exp) => {
        try {
          const res = await financeApi.getJustifications(exp.id)
          const items = Array.isArray(res.data) ? res.data : res.data.results || []
          return items.map((j) => ({
            ...j,
            depense_reference: exp.reference,
            depense_categorie: exp.categorie,
            depense_projet: exp.projet_nom || exp.projet,
          }))
        } catch {
          return []
        }
      })
      const results = await Promise.all(justPromises)
      justifications.value = results.flat()
    } catch (err) {
      error.value = err.response?.data?.detail || "Erreur lors de la récupération des justifications"
    } finally {
      loading.value = false
    }
  }

  const addJustification = async (depenseId, fileOrFormData) => {
    loading.value = true
    error.value = null
    try {
      await financeApi.uploadJustification(depenseId, fileOrFormData)
      await fetchAllJustifications()
    } catch (err) {
      error.value = err.response?.data || "Erreur lors de l'envoi de la pièce justificative"
      throw err
    } finally {
      loading.value = false
    }
  }

  const removeJustification = async (id) => {
    loading.value = true
    error.value = null
    try {
      await financeApi.deleteJustification(id)
      await fetchAllJustifications()
    } catch (err) {
      error.value = err.response?.data || "Erreur lors de la suppression"
      throw err
    } finally {
      loading.value = false
    }
  }

  const fetchAIAnalysis = async (campaignId = null) => {
    loading.value = true
    error.value = null
    try {
      const res = await financeApi.getAIAnalysis(campaignId)
      aiAnalysis.value = res.data
    } catch (err) {
      error.value = err.response?.data?.detail || "Erreur lors de l'analyse IA"
    } finally {
      loading.value = false
    }
  }

  const fetchReports = async (params = {}) => {
    loading.value = true
    error.value = null
    try {
      const res = await financeApi.getFinanceReports(params)
      reportData.value = res.data
    } catch (err) {
      error.value = err.response?.data?.detail || "Erreur lors de la génération du rapport"
    } finally {
      loading.value = false
    }
  }

  const fetchFilters = async () => {
    try {
      const res = await financeApi.getReportFilters()
      filtersData.value = res.data
    } catch {
      // Fallback lookups if needed
    }
  }

  return {
    dashboardData,
    budgets,
    dons,
    depenses,
    justifications,
    aiAnalysis,
    reportData,
    filtersData,
    loading,
    error,
    fetchDashboard,
    fetchBudgets,
    addBudget,
    updateBudget,
    cloturerBudget,
    fetchDonations,
    addDonation,
    fetchExpenses,
    addExpense,
    updateExpenseStatus,
    fetchAllJustifications,
    addJustification,
    removeJustification,
    fetchAIAnalysis,
    fetchReports,
    fetchFilters,
  }
})
