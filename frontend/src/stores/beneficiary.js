import { ref, computed } from "vue"
import { defineStore } from "pinia"
import api, { getErrorMessage } from "@/services/api.js"
import { offlineStorage } from "@/services/offlineStorage.js"

export const useBeneficiaryStore = defineStore("beneficiary", () => {
  const beneficiaries = ref([])
  const currentBeneficiary = ref(null)
  const pendingOffline = ref([])
  const offlineCounts = ref({ total: 0, pending: 0, synced: 0, conflict: 0 })
  const loading = ref(false)
  const error = ref(null)

  const totalBeneficiaries = computed(() => beneficiaries.value.length)

  const fetchBeneficiaries = async () => {
    loading.value = true
    error.value = null
    try {
      const response = await api.get("/api/beneficiaries/")
      beneficiaries.value = response.data
      return response.data
    } catch (err) {
      error.value = getErrorMessage(err)
      throw err
    } finally {
      loading.value = false
    }
  }

  const fetchBeneficiary = async (id) => {
    loading.value = true
    error.value = null
    try {
      const response = await api.get(`/api/beneficiaries/${id}/`)
      currentBeneficiary.value = response.data
      return response.data
    } catch (err) {
      error.value = getErrorMessage(err)
      throw err
    } finally {
      loading.value = false
    }
  }

  const updateBeneficiary = async (id, payload) => {
    loading.value = true
    error.value = null
    try {
      const response = await api.patch(`/api/beneficiaries/${id}/`, payload)
      currentBeneficiary.value = response.data
      await fetchBeneficiaries().catch(() => {})
      return response.data
    } catch (err) {
      error.value = getErrorMessage(err)
      throw err
    } finally {
      loading.value = false
    }
  }

  const updateAIScore = async (id) => {
    loading.value = true
    error.value = null
    try {
      const response = await api.post(`/api/beneficiaries/${id}/ai-score/`)
      if (currentBeneficiary.value?.id === id) {
        currentBeneficiary.value.ai_score = response.data.ai_score
      }
      return response.data
    } catch (err) {
      error.value = getErrorMessage(err)
      throw err
    } finally {
      loading.value = false
    }
  }

  const refreshOfflineCounts = async () => {
    offlineCounts.value = await offlineStorage.getCounts()
    pendingOffline.value = await offlineStorage.getPendingBeneficiaries()
  }

  /**
   * Main submission action for Agents:
   * 1. If online -> send immediately to POST /api/beneficiaries/
   * 2. If offline / network error -> store locally in IndexedDB as PENDING
   */
  const submitBeneficiary = async (payload) => {
    loading.value = true
    error.value = null

    // Check online status
    const isOnline = typeof navigator !== "undefined" ? navigator.onLine : true

    if (isOnline) {
      try {
        const response = await api.post("/api/beneficiaries/", payload)
        await fetchBeneficiaries().catch(() => {})
        return { success: true, offline: false, data: response.data }
      } catch (err) {
        // If 409 duplicate conflict, do not save offline, rethrow with backend message
        if (err.response?.status === 409) {
          const msg = err.response.data?.detail || "Ce bénéficiaire est déjà inscrit dans cette campagne."
          error.value = msg
          const conflictError = new Error(msg)
          conflictError.status = 409
          throw conflictError
        }

        // If other server validation error (400, 403), rethrow
        if (err.response && err.response.status < 500) {
          error.value = getErrorMessage(err)
          throw err
        }

        // Server offline / 5xx error -> fallback to IndexedDB
        await offlineStorage.saveBeneficiary({
          ...payload,
          sync_status: "PENDING",
        })
        await refreshOfflineCounts()
        return {
          success: true,
          offline: true,
          message: "Enregistré hors ligne (serveur temporairement indisponible).",
        }
      } finally {
        loading.value = false
      }
    } else {
      // Offline mode
      try {
        await offlineStorage.saveBeneficiary({
          ...payload,
          sync_status: "PENDING",
        })
        await refreshOfflineCounts()
        return {
          success: true,
          offline: true,
          message: "Enregistré avec succès en mode hors ligne.",
        }
      } finally {
        loading.value = false
      }
    }
  }

  /**
   * Batch synchronization of offline pending records to POST /api/beneficiaries/sync/
   */
  const syncOfflineBeneficiaries = async () => {
    loading.value = true
    error.value = null

    try {
      const pending = await offlineStorage.getPendingBeneficiaries()
      if (pending.length === 0) {
        return { synced: 0, duplicates: 0, failed: 0, message: "Aucun élément en attente." }
      }

      // Format payload for /api/beneficiaries/sync/
      const batchPayload = pending.map((item) => ({
        campagne_id: item.campagne_id,
        formulaire_id: item.formulaire_id,
        zone_id: item.zone_id,
        local_id: item.local_id,
        device_id: item.device_id,
        beneficiary: item.beneficiary,
        responses: item.responses,
      }))

      const response = await api.post("/api/beneficiaries/sync/", batchPayload)
      const result = response.data

      // Update statuses in IndexedDB
      for (const item of pending) {
        // Check in details if this local_id was duplicate or failed
        const detail = result.details?.find((d) => d.local_id === item.local_id)
        if (detail?.status === "DUPLICATE") {
          await offlineStorage.markConflict(item.local_id, detail.reason || "Déjà inscrit")
        } else if (detail?.status === "FAILED") {
          await offlineStorage.markConflict(item.local_id, detail.reason || "Erreur de synchronisation")
        } else {
          await offlineStorage.markSynced(item.local_id, detail?.id)
        }
      }

      await refreshOfflineCounts()
      await fetchBeneficiaries().catch(() => {})

      return result
    } catch (err) {
      error.value = getErrorMessage(err)
      throw err
    } finally {
      loading.value = false
    }
  }

  return {
    beneficiaries,
    currentBeneficiary,
    pendingOffline,
    offlineCounts,
    loading,
    error,
    totalBeneficiaries,
    fetchBeneficiaries,
    fetchBeneficiary,
    updateBeneficiary,
    updateAIScore,
    refreshOfflineCounts,
    submitBeneficiary,
    syncOfflineBeneficiaries,
  }
})

