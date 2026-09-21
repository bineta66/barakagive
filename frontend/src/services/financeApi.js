import api from "@/services/api.js"

export const financeApi = {
  // Dashboard
  getDashboard: () => api.get("/api/finance/dashboard/"),

  // Budgets
  getBudgets: (params = {}) => api.get("/api/finance/budgets/", { params }),
  createBudget: (data) => api.post("/api/finance/budgets/", data),
  updateBudget: (id, data) => api.patch(`/api/finance/budgets/${id}/`, data),
  cloturerBudget: (id) => api.patch(`/api/finance/budgets/${id}/`, { statut: "CLOTURE" }),

  // Dons
  getDonations: (params = {}) => api.get("/api/finance/dons/", { params }),
  createDonation: (data) => api.post("/api/finance/dons/", data),

  // Dépenses
  getExpenses: (params = {}) => api.get("/api/finance/depenses/", { params }),
  createExpense: (data) => api.post("/api/finance/depenses/", data),
  updateExpenseStatus: (id, statut) => api.patch(`/api/finance/depenses/${id}/`, { statut }),

  // Justifications
  getJustifications: (depenseId) => api.get(`/api/finance/depenses/${depenseId}/justifications/`),
  uploadJustification: (depenseId, fileOrFormData) => {
    let payload = fileOrFormData
    let headers = {}
    if (fileOrFormData instanceof File) {
      payload = new FormData()
      payload.append("fichier", fileOrFormData)
      payload.append("type_fichier", fileOrFormData.type || "pdf")
      payload.append("statut", "A_VERIFIER")
      headers = { "Content-Type": "multipart/form-data" }
    } else if (fileOrFormData instanceof FormData) {
      headers = { "Content-Type": "multipart/form-data" }
    }
    return api.post(`/api/finance/depenses/${depenseId}/justifications/`, payload, { headers })
  },
  deleteJustification: (id) => api.delete(`/api/finance/justifications/${id}/`),

  // AI Assistant
  getAIAnalysis: (campaignId) => {
    if (campaignId) {
      return api.get(`/api/finance/ia/budget-analysis/${campaignId}/`)
    }
    return api.get("/api/assistant/dashboard/")
  },

  // Reports
  getFinanceReports: (params = {}) => api.get("/api/reports/finance/", { params }),
  getReportFilters: () => api.get("/api/reports/filters/"),
  exportPDF: (params = {}) => api.get("/api/reports/export/pdf/", { params, responseType: "blob" }),
  exportExcel: (params = {}) => api.get("/api/reports/export/excel/", { params, responseType: "blob" }),

  // Lookups
  getProjects: () => api.get("/api/projects/"),
  getCampaigns: () => api.get("/api/campaigns/"),
}

export default financeApi
