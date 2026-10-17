import { ref, computed } from "vue"
import { defineStore } from "pinia"
import api, { getErrorMessage } from "@/services/api.js"

export const useOrganisationRequestStore = defineStore("organisationRequest", () => {
  const requests = ref([])
  const currentRequest = ref(null)
  const loading = ref(false)
  const error = ref(null)
  const successMessage = ref(null)

  // ── Computed ────────────────────────────────────────────────────────────
  const pendingRequests = computed(() =>
    requests.value.filter((r) => r.statut === "EN_ATTENTE")
  )

  const approvedRequests = computed(() =>
    requests.value.filter((r) => r.statut === "APPROUVEE")
  )

  const rejectedRequests = computed(() =>
    requests.value.filter((r) => r.statut === "REJETEE")
  )

  // ── Actions ─────────────────────────────────────────────────────────────

  /**
   * GET /api/superadmin/organisations/
   * Récupère toutes les demandes d'inscription ONG
   */
  const getPendingRequests = async () => {
    loading.value = true
    error.value = null
    try {
      const response = await api.get("/api/superadmin/organisations/")
      requests.value = response.data
      return response.data
    } catch (e) {
      error.value = getErrorMessage(e)
      throw e
    } finally {
      loading.value = false
    }
  }

  /**
   * GET /api/superadmin/organisations/:id/
   * Récupère le détail d'une demande avec le rapport IA
   */
  const getRequestDetail = async (id) => {
    loading.value = true
    error.value = null
    try {
      const response = await api.get(`/api/superadmin/organisations/${id}/`)
      currentRequest.value = response.data
      return response.data
    } catch (e) {
      error.value = getErrorMessage(e)
      throw e
    } finally {
      loading.value = false
    }
  }

  /**
   * PATCH /api/superadmin/organisations/:id/decision/
   * Approuver une demande d'inscription ONG
   */
  const approveRequest = async (id) => {
    loading.value = true
    error.value = null
    successMessage.value = null
    try {
      const response = await api.patch(`/api/superadmin/organisations/${id}/decision/`, {
        decision: "APPROUVEE",
      })
      successMessage.value = response.data.message || "ONG approuvée avec succès."

      // Mettre à jour localement
      if (currentRequest.value && currentRequest.value.id === id) {
        currentRequest.value.statut = "APPROUVEE"
      }
      const idx = requests.value.findIndex((r) => r.id === id)
      if (idx !== -1) {
        requests.value[idx].statut = "APPROUVEE"
      }

      return response.data
    } catch (e) {
      error.value = getErrorMessage(e)
      throw e
    } finally {
      loading.value = false
    }
  }

  /**
   * PATCH /api/superadmin/organisations/:id/decision/
   * Rejeter une demande d'inscription ONG
   */
  const rejectRequest = async (id, motif = "") => {
    loading.value = true
    error.value = null
    successMessage.value = null
    try {
      const response = await api.patch(`/api/superadmin/organisations/${id}/decision/`, {
        decision: "REJETEE",
        motif,
      })
      successMessage.value = response.data.message || "Demande rejetée."

      // Mettre à jour localement
      if (currentRequest.value && currentRequest.value.id === id) {
        currentRequest.value.statut = "REJETEE"
      }
      const idx = requests.value.findIndex((r) => r.id === id)
      if (idx !== -1) {
        requests.value[idx].statut = "REJETEE"
      }

      return response.data
    } catch (e) {
      error.value = getErrorMessage(e)
      throw e
    } finally {
      loading.value = false
    }
  }

  const clearMessages = () => {
    error.value = null
    successMessage.value = null
  }

  return {
    requests,
    currentRequest,
    loading,
    error,
    successMessage,
    pendingRequests,
    approvedRequests,
    rejectedRequests,
    getPendingRequests,
    getRequestDetail,
    approveRequest,
    rejectRequest,
    clearMessages,
  }
})
