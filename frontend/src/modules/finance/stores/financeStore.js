import { ref } from "vue"
import { defineStore } from "pinia"
import { financeService } from "@/modules/finance/services/financeService.js"

export const useFinanceStore = defineStore("finance", () => {
  const dashboard = ref(null)
  const budgets = ref([])
  const dons = ref([])
  const depenses = ref([])
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
      budgets.value = response.data
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
      dons.value = response.data
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
      depenses.value = response.data
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
    ])
  }

  const createBudget = async (data) => {
    await financeService.createBudget(data)
    await fetchBudgets()
  }

  const createDonation = async (data) => {
    await financeService.createDonation(data)
    await fetchDonations()
    await fetchBudgets()
  }

  const createExpense = async (data) => {
    await financeService.createExpense(data)
    await fetchExpenses()
    await fetchBudgets()
  }

  const uploadJustification = async (expenseId, file) => {
    await financeService.uploadJustification(expenseId, file)
    await fetchExpenses()
  }

  return {
    dashboard,
    budgets,
    dons,
    depenses,
    loading,
    error,
    fetchDashboard,
    fetchBudgets,
    fetchDonations,
    fetchExpenses,
    refreshAll,
    createBudget,
    createDonation,
    createExpense,
    uploadJustification,
  }
})