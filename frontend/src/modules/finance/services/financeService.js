import api from "@/services/api.js"

export const financeService = {
  fetchDashboard: () => api.get("/api/finance/dashboard/"),
  fetchBudgets: () => api.get("/api/finance/budgets/"),
  fetchBudgetLines: () => api.get("/api/finance/lignes-budgetaires/"),
  createBudgetLine: (payload) => api.post("/api/finance/lignes-budgetaires/", payload),
  fetchFinancements: () => api.get("/api/finance/financements/"),
  createFinancement: (payload) => api.post("/api/finance/financements/", payload),
  fetchDonations: () => api.get("/api/finance/dons/"),
  createDonor: (payload) => api.post("/api/finance/donateurs/", payload),
  fetchExpenses: () => api.get("/api/finance/depenses/"),
  fetchBailleurs: () => api.get("/api/finance/bailleurs/"),
  fetchBudgetAnalysis: (campaignId) => api.get(`/api/finance/budget-analysis/${campaignId}/`),
  createBudget: (payload) => api.post("/api/finance/budgets/", payload),
  updateBudget: (id, payload) => api.patch(`/api/finance/budgets/${id}/`, payload),
  deleteBudget: (id) => api.delete(`/api/finance/budgets/${id}/`),
  createDonation: (payload) => api.post("/api/finance/dons/", payload),
  updateDonation: (id, payload) => api.patch(`/api/finance/dons/${id}/`, payload),
  deleteDonation: (id) => api.delete(`/api/finance/dons/${id}/`),
  createExpense: (payload) => api.post("/api/finance/depenses/", payload),

  // Dépense détail / update / delete
  fetchExpense: (id) => api.get(`/api/finance/depenses/${id}/`),
  updateExpense: (id, payload) => api.patch(`/api/finance/depenses/${id}/`, payload),
  deleteExpense: (id) => api.delete(`/api/finance/depenses/${id}/`),

  // Justifications
  uploadJustification: (expenseId, file, type_fichier) => {
    const formData = new FormData()
    formData.append("fichier", file)
    formData.append("type_fichier", type_fichier || "")
    return api.post(`/api/finance/depenses/${expenseId}/justifications/`, formData, {
      headers: {
        "Content-Type": "multipart/form-data"
      }
    })
  },
  fetchJustifications: (expenseId) => api.get(`/api/finance/depenses/${expenseId}/justifications/`),
  deleteJustification: (justificationId) => api.delete(`/api/finance/justifications/${justificationId}/`),
}
