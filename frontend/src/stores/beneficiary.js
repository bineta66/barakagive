import { ref, computed, inject } from 'vue'
import { defineStore } from 'pinia'
import api, { getErrorMessage } from '@/services/api.js'
import { offlineStorage } from '@/services/offlineStorage.js'

export const useBeneficiaryStore = defineStore('beneficiary', () => {
  const beneficiaries = ref([])
  const currentBeneficiary = ref(null)
  const offlineCounts = ref({ total: 0, enAttente: 0, synchronise: 0 })
  const loading = ref(false)
  const syncing = ref(false)   // true pendant une sync auto en cours
  const error = ref(null)
  const pagination = ref({ count: 0, next: null, previous: null })
  const beneficiaryQuery = ref({ page: 1, page_size: 20 })

  const totalBeneficiaries = computed(() => beneficiaries.value.length)

  // ── Fetch serveur ──────────────────────────────────────────────────────
  const fetchBeneficiaries = async (params = null) => {
    if (params) beneficiaryQuery.value = { ...beneficiaryQuery.value, ...params }
    loading.value = true
    error.value = null
    try {
      const res = await api.get('/api/beneficiaries/', { params: beneficiaryQuery.value })
      const data = res.data
      beneficiaries.value = data?.results ?? (Array.isArray(data) ? data : [])
      pagination.value = Array.isArray(data)
        ? { count: data.length, next: null, previous: null }
        : { count: data?.count || 0, next: data?.next || null, previous: data?.previous || null }
      return beneficiaries.value
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
      const res = await api.get(`/api/beneficiaries/${id}/`)
      currentBeneficiary.value = res.data
      return res.data
    } catch (err) {
      error.value = getErrorMessage(err)
      throw err
    } finally {
      loading.value = false
    }
  }

  const fetchHumanitarianActions = async (beneficiaryId) => {
    const res = await api.get(`/api/beneficiaries/${beneficiaryId}/actions/`)
    return res.data
  }

  const createHumanitarianAction = async (beneficiaryId, payload) => {
    const res = await api.post(`/api/beneficiaries/${beneficiaryId}/actions/`, payload)
    return res.data
  }

  const updateBeneficiary = async (id, payload) => {
    loading.value = true
    error.value = null
    try {
      const res = await api.patch(`/api/beneficiaries/${id}/`, payload)
      currentBeneficiary.value = res.data
      await fetchBeneficiaries().catch(() => { })
      return res.data
    } catch (err) {
      error.value = getErrorMessage(err)
      throw err
    } finally {
      loading.value = false
    }
  }

  const updateVulnerabilityScore = async (id) => {
    loading.value = true
    error.value = null
    try {
      const res = await api.post(`/api/beneficiaries/${id}/vulnerability-score/`)
      if (currentBeneficiary.value?.id === id) {
        currentBeneficiary.value.score_vulnerabilite = res.data.score_vulnerabilite
      }
      return res.data
    } catch (err) {
      error.value = getErrorMessage(err)
      throw err
    } finally {
      loading.value = false
    }
  }

  // ── Refresh compteurs hors-ligne ───────────────────────────────────────
  const refreshOfflineCounts = async () => {
    offlineCounts.value = await offlineStorage.getCounts()
  }

  // ── Soumission principale de l'agent ──────────────────────────────────
  /**
   * Si en ligne  → envoi immédiat au serveur
   * Si hors ligne → sauvegarde locale PENDING (statut anglais)
   *
   * Utilise connectionStatus fourni par App.vue via provide/inject,
   * pas navigator.onLine (qui peut retourner de faux positifs).
   *
   * Retourne :
   *   { offline: false }  → envoyé au serveur
   *   { offline: true  }  → sauvegardé localement
   */
  const submitBeneficiary = async (payload, isOnlineParam = null) => {
    loading.value = true
    error.value = null

    let enLigne
    if (typeof isOnlineParam === 'boolean') {
      enLigne = isOnlineParam
    } else if (typeof payload.is_online === 'boolean') {
      enLigne = payload.is_online
    } else {
      let connectionStatus
      try {
        connectionStatus = inject('connectionStatus', null)
      } catch {
        connectionStatus = null
      }
      enLigne = connectionStatus ? connectionStatus.value === 'online' : (typeof navigator !== 'undefined' && navigator.onLine)
    }

    if (enLigne) {
      try {
        const res = await api.post('/api/beneficiaries/', payload)
        await fetchBeneficiaries().catch(() => { })
        return { success: true, offline: false, data: res.data }

      } catch (err) {
        // Doublon → erreur métier, ne pas sauvegarder hors ligne
        if (err.response?.status === 409) {
          const msg = err.response.data?.detail || 'Ce bénéficiaire est déjà inscrit dans cette campagne.'
          error.value = msg
          const e = new Error(msg)
          e.status = 409
          loading.value = false
          throw e
        }

        // Erreur de validation (400/403) → remonter l'erreur
        if (err.response && err.response.status < 500) {
          error.value = getErrorMessage(err)
          loading.value = false
          throw err
        }

        // Serveur inaccessible / 5xx → basculer en hors ligne
        await offlineStorage.saveBeneficiary({ ...payload, sync_status: 'PENDING' })
        await refreshOfflineCounts()
        loading.value = false
        return { success: true, offline: true }
      }
    } else {
      // Hors ligne → stockage local avec statut PENDING
      await offlineStorage.saveBeneficiary({ ...payload, sync_status: 'PENDING' })
      await refreshOfflineCounts()
      loading.value = false
      return { success: true, offline: true }
    }
  }

  // ── Synchronisation automatique ────────────────────────────────────────
  /**
   * Appelée automatiquement dès que la connexion revient (depuis App.vue).
   * Envoie tous les bénéficiaires EN_ATTENTE vers le serveur.
   * Marque SYNCHRONISE uniquement après confirmation serveur.
   * L'agent n'a rien à faire.
   */
  const syncOfflineBeneficiaries = async () => {
    if (syncing.value) return { synced: 0, failed: 0, conflict: 0 }

    const pending = await offlineStorage.getPendingBeneficiaries()
    if (pending.length === 0) return { synced: 0, failed: 0, conflict: 0 }

    syncing.value = true
    error.value = null

    let synced = 0
    let failed = 0
    let conflict = 0

    try {
      // Envoi item par item vers pwa-sync
      for (const item of pending) {
        // Marquer SYNCING
        await offlineStorage.updateStatus(item.local_id, 'SYNCING')

        const payload = {
          local_id: item.local_id,
          campagne_id: item.campagne_id,
          formulaire_id: item.formulaire_id,
          zone_id: item.zone_id,
          beneficiary: item.beneficiary,
          responses: item.responses || [],
        }

        try {
          const res = await api.post('/api/beneficiaries/pwa-sync/', payload)
          await offlineStorage.updateStatus(item.local_id, 'SYNCED', {
            server_id: res.data?.id,
            error_message: null,
          })
          synced++
        } catch (itemErr) {
          let errorMsg = 'Erreur inconnue'
          if (itemErr.response?.data?.detail) {
            errorMsg = itemErr.response.data.detail
          } else if (itemErr.response?.data?.beneficiary) {
            const bErr = itemErr.response.data.beneficiary
            errorMsg = Object.entries(bErr)
              .map(([k, v]) => `${k}: ${Array.isArray(v) ? v.join(', ') : v}`)
              .join(' | ')
          } else if (itemErr.response?.data && typeof itemErr.response.data === 'object') {
            errorMsg = Object.entries(itemErr.response.data)
              .map(([k, v]) => `${k}: ${Array.isArray(v) ? v.join(', ') : v}`)
              .join(' | ')
          } else if (itemErr.message) {
            errorMsg = itemErr.message
          }

          if (itemErr.response?.status === 409) {
            // Doublon → CONFLICT
            await offlineStorage.updateStatus(item.local_id, 'CONFLICT', {
              error_message: errorMsg,
            })
            conflict++
          } else {
            // Autre erreur → FAILED
            await offlineStorage.updateStatus(item.local_id, 'FAILED', {
              error_message: errorMsg,
            })
            failed++
          }
        }
      }

      await refreshOfflineCounts()
      if (synced > 0) await fetchBeneficiaries().catch(() => { })

      return { synced, failed, conflict }

    } finally {
      syncing.value = false
    }
  }

  // ── Vérification doublon (utilisé par CollecteTerrain) ──────────────────
  const checkDuplicate = async ({ campagne_id, zone_id, nom, prenom, telephone }) => {
    try {
      const res = await api.get('/api/beneficiaries/check-duplicate/', {
        params: { campagne_id, zone_id, nom, prenom, telephone }
      })
      return res.data?.exists === true
    } catch {
      return false
    }
  }

  return {
    beneficiaries,
    pagination,
    beneficiaryQuery,
    currentBeneficiary,
    offlineCounts,
    loading,
    syncing,
    error,
    totalBeneficiaries,
    fetchBeneficiaries,
    fetchBeneficiary,
    fetchHumanitarianActions,
    createHumanitarianAction,
    updateBeneficiary,
    updateVulnerabilityScore,
    refreshOfflineCounts,
    submitBeneficiary,
    syncOfflineBeneficiaries,
    checkDuplicate,
    // Rétro-compat
    pendingOffline: ref([]),
  }
})
