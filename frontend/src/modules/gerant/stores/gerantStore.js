import { ref, computed } from "vue"
import { defineStore } from "pinia"
import api, { getErrorMessage } from "@/services/api.js"

export const useGerantStore = defineStore("gerant", () => {
  const users = ref([])
  const projets = ref([])
  const campaigns = ref([])
  const beneficiaries = ref([])
  const loading = ref(false)
  const error = ref(null)

  const partenaires = ref([])
  const bailleurs = ref([])
  const budgetsEnAttente = ref([])
  const decisionDashboard = ref(null)
  const usersPagination = ref({ count: 0, next: null, previous: null })
  const usersQuery = ref({ page: 1, page_size: 20 })

  const chefsProjet = computed(() => users.value.filter((u) => u.role === "CHEF_PROJET"))
  const responsablesFinance = computed(() => users.value.filter((u) => u.role === "FINANCE"))
  const agents = computed(() => users.value.filter((u) => u.role === "AGENT"))

  const statistiques = computed(() => {
    const totalProj = projets.value.filter((p) => !p.archived).length
    const totalUsers = usersPagination.value.count || users.value.length
    const budgetTot = projets.value.reduce(
      (acc, p) => acc + (parseFloat(p.budget) || 0),
      0
    )
    const activeCamp = campaigns.value.length
    const totalBenef = beneficiaries.value.length

    return {
      totalProjets: totalProj,
      totalUtilisateurs: totalUsers,
      totalCampagnes: activeCamp,
      totalBeneficiaires: totalBenef,
      budgetTotal: budgetTot,
      chefsProjetCount: chefsProjet.value.length,
      financeCount: responsablesFinance.value.length,
      agentsCount: agents.value.length,
    }
  })

  const formatMontant = (montant) => {
    if (!montant) return "0"
    return parseFloat(montant).toLocaleString("fr-FR")
  }

  const fetchUsers = async (params = null) => {
    if (params) usersQuery.value = { ...usersQuery.value, ...params }
    loading.value = true
    error.value = null
    try {
      const response = await api.get("/api/accounts/users/", { params: usersQuery.value })
      const data = response.data
      users.value = data?.results ?? data
      usersPagination.value = Array.isArray(data)
        ? { count: data.length, next: null, previous: null }
        : { count: data?.count || 0, next: data?.next || null, previous: data?.previous || null }
      return users.value
    } catch (e) {
      error.value = getErrorMessage(e)
      throw e
    } finally {
      loading.value = false
    }
  }

  const createUser = async (payload) => {
    loading.value = true
    error.value = null
    try {
      const response = await api.post("/api/accounts/users/create/", payload)
      await fetchUsers().catch(() => { })
      return response.data
    } catch (e) {
      error.value = getErrorMessage(e)
      throw e
    } finally {
      loading.value = false
    }
  }

  const updateUser = async (id, payload) => {
    loading.value = true
    error.value = null
    try {
      const response = await api.patch(`/api/accounts/users/${id}/`, payload)
      await fetchUsers().catch(() => {})
      return response.data
    } catch (e) {
      error.value = getErrorMessage(e)
      throw e
    } finally {
      loading.value = false
    }
  }

  const toggleUserStatus = async (id, isCurrentlyActive) => {
    loading.value = true
    error.value = null
    try {
      const newStatus = isCurrentlyActive ? "SUSPENDED" : "ACTIVE"
      const response = await api.patch(`/api/accounts/users/${id}/`, {
        status: newStatus,
        is_active: !isCurrentlyActive,
      })
      const idx = users.value.findIndex((u) => u.id === id)
      if (idx !== -1) {
        users.value[idx] = { ...users.value[idx], ...response.data }
      }
      return response.data
    } catch (e) {
      error.value = getErrorMessage(e)
      throw e
    } finally {
      loading.value = false
    }
  }

  const fetchUserDetail = async (id) => {
    try {
      const response = await api.get(`/api/accounts/users/${id}/`)
      return response.data
    } catch (e) {
      error.value = getErrorMessage(e)
      throw e
    }
  }

  const fetchProjets = async () => {
    try {
      const response = await api.get("/api/projects/")
      projets.value = response.data?.results ?? response.data
      return projets.value
    } catch (e) {
      error.value = getErrorMessage(e)
      return []
    }
  }

  const deleteProject = async (id) => {
    try {
      await api.delete(`/api/projects/${id}/`)
      await fetchProjets()
    } catch (e) {
      error.value = getErrorMessage(e)
      throw e
    }
  }

  const fetchCampaigns = async () => {
    try {
      const response = await api.get("/api/campaigns/")
      campaigns.value = response.data?.results ?? response.data
      return campaigns.value
    } catch (e) {
      error.value = getErrorMessage(e)
      return []
    }
  }

  const fetchDecisionDashboard = async () => {
    try {
      const response = await api.get("/api/projects/dashboard/")
      decisionDashboard.value = response.data
      return response.data
    } catch (e) {
      error.value = getErrorMessage(e)
      return null
    }
  }

  const fetchBeneficiaries = async () => {
    try {
      const response = await api.get("/api/beneficiaries/")
      beneficiaries.value = response.data?.results ?? response.data
      return beneficiaries.value
    } catch (e) {
      error.value = getErrorMessage(e)
      return []
    }
  }

  const fetchBailleurs = async () => {
    try {
      const response = await api.get("/api/finance/bailleurs/")
      bailleurs.value = response.data.map((item) => ({
        ...item,
        contact: item.email || item.telephone || "",
        statut: item.actif ? "Reçu" : "En attente",
      }))
      return bailleurs.value
    } catch (e) {
      error.value = getErrorMessage(e)
      return []
    }
  }

  const fetchPartenaires = async () => {
    try {
      const response = await api.get("/api/finance/partenaires/")
      partenaires.value = response.data.map((item) => ({
        ...item,
        contact: item.email || item.telephone || "",
        statut: item.actif ? "ACTIF" : "INACTIF",
        zone: item.adresse || "",
        projet: "",
      }))
      return partenaires.value
    } catch (e) {
      error.value = getErrorMessage(e)
      return []
    }
  }

  const saveBailleurApi = async (data, id = null) => {
    const payload = {
      nom: data.nom,
      type: data.type || "",
      email: data.email || data.contact || "",
      telephone: data.telephone || "",
      adresse: data.adresse || "",
      actif: data.statut !== "En attente",
    }
    if (id) await api.patch(`/api/finance/bailleurs/${id}/`, payload)
    else await api.post("/api/finance/bailleurs/", payload)
    return fetchBailleurs()
  }

  const savePartenaireApi = async (data, id = null) => {
    const payload = {
      nom: data.nom,
      domaine: data.domaine || "",
      email: data.email || data.contact || "",
      telephone: data.telephone || "",
      adresse: data.adresse || data.zone || "",
      actif: data.statut !== "INACTIF",
    }
    if (id) await api.patch(`/api/finance/partenaires/${id}/`, payload)
    else await api.post("/api/finance/partenaires/", payload)
    return fetchPartenaires()
  }

  const deleteBailleurApi = async (id) => {
    await api.delete(`/api/finance/bailleurs/${id}/`)
    return fetchBailleurs()
  }

  const deletePartenaireApi = async (id) => {
    await api.delete(`/api/finance/partenaires/${id}/`)
    return fetchPartenaires()
  }

  // Budgets en attente d'approbation
  const fetchBudgetsToApprove = async () => {
    try {
      const response = await api.get("/api/finance/budgets/approval/")
      budgetsEnAttente.value = response.data
      return response.data
    } catch (e) {
      error.value = getErrorMessage(e)
      return []
    }
  }

  const approveBudget = async (budgetId, action) => {
    try {
      await api.post("/api/finance/budgets/approval/", {
        budget_id: budgetId,
        action: action,
      })
      return fetchBudgetsToApprove()
    } catch (e) {
      error.value = getErrorMessage(e)
      throw e
    }
  }

  const fetchAll = async () => {
    loading.value = true
    error.value = null
    try {
      await Promise.allSettled([
        fetchUsers(),
        fetchProjets(),
        fetchCampaigns(),
        fetchBeneficiaries(),
        fetchDecisionDashboard(),
        fetchBailleurs(),
        fetchPartenaires(),
      ])
    } finally {
      loading.value = false
    }
  }

  return {
    users,
    usersPagination,
    usersQuery,
    projets,
    campaigns,
    beneficiaries,
    partenaires,
    bailleurs,
    budgetsEnAttente,
    decisionDashboard,
    chefsProjet,
    responsablesFinance,
    agents,
    statistiques,
    loading,
    error,
    formatMontant,
    fetchUsers,
    createUser,
    updateUser,
    toggleUserStatus,
    fetchUserDetail,
    fetchProjets,
    deleteProject,
    fetchCampaigns,
    fetchDecisionDashboard,
    fetchBeneficiaries,
    fetchBailleurs,
    fetchPartenaires,
    saveBailleurApi,
    savePartenaireApi,
    deleteBailleurApi,
    deletePartenaireApi,
    fetchBudgetsToApprove,
    approveBudget,
    fetchAll,
  }
})
