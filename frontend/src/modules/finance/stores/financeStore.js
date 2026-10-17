import { ref } from "vue"
import { defineStore } from "pinia"
import { financeService } from "@/modules/finance/services/financeService.js"

export const useFinanceStore = defineStore("finance", () => {
  const dashboard = ref(null)
  const budgets = ref([])
  const dons = ref([])
  const depenses = ref([])
  const bailleurs = ref([])
  const loading = ref(false)
  const error = ref(null)

  const fetchDashboard = async () => {
    loading.value = true
    error.value = null
    try {
      const response = await financeService.fetchDashboard()
      dashboard.value = response.data
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  const fetchBudgets = async () => {
    loading.value = true
    error.value = null
    try {
      const response = await financeService.fetchBudgets()
      budgets.value =
        response.data?.results ??
        (Array.isArray(response.data) ? response.data : [])
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  const fetchDonations = async () => {
    loading.value = true
    error.value = null
    try {
      const response = await financeService.fetchDonations()
      dons.value =
        response.data?.results ??
        (Array.isArray(response.data) ? response.data : [])
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  const fetchExpenses = async () => {
    loading.value = true
    error.value = null
    try {
      const response = await financeService.fetchExpenses()
      depenses.value =
        response.data?.results ??
        (Array.isArray(response.data) ? response.data : [])
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  const fetchBailleurs = async () => {
    loading.value = true
    error.value = null
    try {
      const response = await financeService.fetchBailleurs()
      bailleurs.value =
        response.data?.results ??
        (Array.isArray(response.data) ? response.data : [])
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  const refreshAll = async () => {
    await Promise.all([
      fetchDashboard(),
      fetchBudgets(),
      fetchDonations(),
      fetchExpenses(),
      fetchBailleurs(),
    ])
  }

  const createBudget = async (data) => {
    await financeService.createBudget(data)
    await fetchBudgets()
  }

  const updateBudget = async (id, data) => {
    await financeService.updateBudget(id, data)
    await fetchBudgets()
  }

  const deleteBudget = async (id) => {
    await financeService.deleteBudget(id)
    await fetchBudgets()
  }

  const createDonation = async (data) => {
    await financeService.createDonation(data)
    await fetchDonations()
    await fetchBudgets()
  }

  const updateDonation = async (id, data) => {
    await financeService.updateDonation(id, data)
    await fetchDonations()
    await fetchBudgets()
  }

  const deleteDonation = async (id) => {
    await financeService.deleteDonation(id)
    await fetchDonations()
    await fetchBudgets()
  }

  const createExpense = async (data) => {
    await financeService.createExpense(data)
    await fetchExpenses()
    await fetchBudgets()
  }

  const updateExpense = async (id, data) => {
    await financeService.updateExpense(id, data)
    await fetchExpenses()
  }

  const deleteExpense = async (id) => {
    await financeService.deleteExpense(id)
    await fetchExpenses()
    await fetchBudgets()
  }

  const uploadJustification = async (expenseId, file, type_fichier) => {
    await financeService.uploadJustification(expenseId, file, type_fichier)
    await fetchExpenses()
  }

  const deleteJustification = async (justificationId) => {
    await financeService.deleteJustification(justificationId)
    await fetchExpenses()
  }

  return {
    dashboard,
    budgets,
    dons,
    depenses,
    bailleurs,
    loading,
    error,
    fetchDashboard,
    fetchBudgets,
    fetchDonations,
    fetchExpenses,
    fetchBailleurs,
    refreshAll,
    createBudget,
    updateBudget,
    deleteBudget,
    createDonation,
    updateDonation,
    deleteDonation,
    createExpense,
    updateExpense,
    deleteExpense,
    uploadJustification,
    deleteJustification,
  }
})