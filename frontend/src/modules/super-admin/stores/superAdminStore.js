import { ref, computed } from "vue"
import { defineStore } from "pinia"
import api, { getErrorMessage } from "@/services/api.js"

export const useSuperAdminStore = defineStore("superAdmin", () => {
  const ongs = ref([])
  const loading = ref(false)
  const error = ref(null)
  const dashboard = ref(null)
  const dashboardLoading = ref(false)
  const dashboardError = ref(null)

  const fetchDashboard = async (period = "30d") => {
    dashboardLoading.value = true
    dashboardError.value = null
    try {
      const response = await api.get("/api/superadmin/dashboard/", { params: { period } })
      dashboard.value = response.data
      return response.data
    } catch (e) {
      dashboardError.value = getErrorMessage(e)
      throw e
    } finally {
      dashboardLoading.value = false
    }
  }

  const demandesONG = computed(() => {
    return ongs.value.filter((o) => o.status === "EN_ATTENTE")
  })

  const ongsActives = computed(() => {
    return ongs.value.filter((o) => o.status === "ACTIVE")
  })

  const statistiques = computed(() => {
    const regionsCount = new Set(ongs.value.map((o) => o.region).filter(Boolean)).size

    return {
      regionsCount,
    }
  })

  const formatMontant = (montant) => {
    if (!montant) return "0"
    return montant.toLocaleString("fr-FR")
  }

  const fetchAll = async () => {
    loading.value = true
    error.value = null
    try {
      const response = await api.get("/api/organizations/")
      ongs.value = response.data
      return response.data
    } catch (e) {
      error.value = getErrorMessage(e)
      throw e
    } finally {
      loading.value = false
    }
  }

  const createONG = async (payload) => {
    loading.value = true
    error.value = null
    try {
      const requestPayload = new FormData()
      Object.entries(payload).forEach(([key, value]) => {
        if (value !== null && value !== undefined && value !== "") {
          requestPayload.append(key, value)
        }
      })

      const response = await api.post("/api/organizations/register/", requestPayload)
      await fetchAll().catch(() => { })
      return response.data
    } catch (e) {
      error.value = getErrorMessage(e)
      throw e
    } finally {
      loading.value = false
    }
  }

  const approveONG = async (id) => {
    loading.value = true
    error.value = null
    try {
      await api.post(`/api/organizations/admin/${id}/approve/`)
      await fetchAll().catch(() => { })
    } catch (e) {
      error.value = getErrorMessage(e)
      throw e
    } finally {
      loading.value = false
    }
  }

  const rejectONG = async (id) => {
    loading.value = true
    error.value = null
    try {
      await api.post(`/api/organizations/admin/${id}/reject/`)
      await fetchAll().catch(() => { })
    } catch (e) {
      error.value = getErrorMessage(e)
      throw e
    } finally {
      loading.value = false
    }
  }

  // Liste des gérunts de toutes les ONG
  const gerants = ref([])

  const fetchGerants = async () => {
    loading.value = true
    error.value = null
    try {
      const response = await api.get("/api/accounts/gerants/")
      gerants.value = response.data
      return response.data
    } catch (e) {
      error.value = getErrorMessage(e)
      throw e
    } finally {
      loading.value = false
    }
  }

  // ── Abonnements (Super Admin) ──────────────────────────────
  const abonnements = ref([])
  const loadingAbonnements = ref(false)

  const statsAbonnements = computed(() => {
    const actifs = abonnements.value.filter(a => a.statut === "ACTIVE").length
    const expires = abonnements.value.filter(a => a.statut === "EXPIRED").length
    const suspendus = abonnements.value.filter(a => a.statut === "CANCELLED").length
    const essai = abonnements.value.filter(a => a.statut === "TRIAL").length
    const revenu = actifs * 50000
    return { actifs, expires, suspendus, essai, revenu, total: abonnements.value.length }
  })

  const fetchAbonnements = async () => {
    loadingAbonnements.value = true
    error.value = null
    try {
      const response = await api.get("/api/payment/admin/subscriptions/")
      abonnements.value = response.data
      return response.data
    } catch (e) {
      error.value = getErrorMessage(e)
    } finally {
      loadingAbonnements.value = false
    }
  }

  const suspendreAbonnement = async (id) => {
    try {
      await api.post(`/api/payment/admin/subscriptions/${id}/suspend/`)
      await fetchAbonnements()
    } catch (e) {
      error.value = getErrorMessage(e)
      throw e
    }
  }

  const reactiverAbonnement = async (id) => {
    try {
      await api.post(`/api/payment/admin/subscriptions/${id}/reactivate/`)
      await fetchAbonnements()
    } catch (e) {
      error.value = getErrorMessage(e)
      throw e
    }
  }

  const fetchAbonnementDetail = async (id) => {
    try {
      const response = await api.get(`/api/payment/admin/subscriptions/${id}/`)
      return response.data
    } catch (e) {
      error.value = getErrorMessage(e)
      throw e
    }
  }

  return {
    ongs,
    demandesONG,
    ongsActives,
    statistiques,
    formatMontant,
    loading,
    error,
    dashboard,
    dashboardLoading,
    dashboardError,
    fetchDashboard,
    fetchAll,
    createONG,
    approveONG,
    rejectONG,
    gerants,
    fetchGerants,
    abonnements,
    loadingAbonnements,
    statsAbonnements,
    fetchAbonnements,
    suspendreAbonnement,
    reactiverAbonnement,
    fetchAbonnementDetail,
  }
})


