import api from "@/services/api.js"

export const financeService = {
  fetchDashboard: () => api.get("/api/finance/dashboard/"),
  fetchBudgets: () => api.get("/api/finance/budgets/"),
  fetchDonations: () => api.get("/api/finance/dons/"),
  fetchExpenses: () => api.get("/api/finance/depenses/"),
  fetchBudgetAnalysis: (campaignId) => api.get(`/api/finance/budget-analysis/${campaignId}/`),
  createBudget: (payload) => api.post("/api/finance/budgets/", payload),
  createDonation: (payload) => api.post("/api/finance/dons/", payload),
  createExpense: (payload) => api.post("/api/finance/depenses/", payload),
  uploadJustification: (expenseId, file) => {
    const formData = new FormData()
    formData.append("fichier", file)
    return api.post(`/api/finance/depenses/${expenseId}/justifications/`, formData, {
      headers: { "Content-Type": "multipart/form-data" },
    })
  },
}