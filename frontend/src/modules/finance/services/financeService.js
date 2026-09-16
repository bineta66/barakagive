import api from "@/services/api.js"

const list = async (path) => {
  const response = await api.get(path)
  return response.data
}

export const financeService = {
  fetchDashboard: () => list("/api/finance/dashboard/finance/"),
  fetchProjects: () => list("/api/projects/"),
  fetchProject: (id) => list(`/api/projects/${id}/`),
  fetchBudgets: () => list("/api/finance/budgets/"),
  fetchDonations: () => list("/api/finance/dons/"),
  fetchFunders: () => list("/api/finance/bailleurs/"),
  createFunder: (payload) => api.post("/api/finance/bailleurs/", payload),
  fetchExpenses: () => list("/api/finance/depenses/"),
  createBudget: (payload) => api.post("/api/finance/budgets/", payload),
  updateBudget: (id, payload) => api.patch(`/api/finance/budgets/${id}/`, payload),
  createDonation: (payload) => api.post("/api/finance/dons/", payload),
  updateDonation: (id, payload) => api.patch(`/api/finance/dons/${id}/`, payload),
  deleteDonation: (id) => api.delete(`/api/finance/dons/${id}/`),
  createExpense: (payload) => api.post("/api/finance/depenses/", payload),
  updateExpense: (id, payload) => api.patch(`/api/finance/depenses/${id}/`, payload),
  uploadJustification: (expenseId, file) => {
    const formData = new FormData()
    formData.append("fichier", file)
    return api.post(`/api/finance/depenses/${expenseId}/justificatifs/`, formData, {
      headers: { "Content-Type": "multipart/form-data" },
    })
  },
}
