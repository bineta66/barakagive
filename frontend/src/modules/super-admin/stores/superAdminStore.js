import { ref, computed } from "vue"
import { defineStore } from "pinia"
import api, { getErrorMessage } from "@/services/api.js"

export const useSuperAdminStore = defineStore("superAdmin", () => {
  const ongs = ref([])
  const loading = ref(false)
  const error = ref(null)

  const demandesONG = computed(() => {
    return ongs.value.filter((o) => o.status === "EN_ATTENTE")
  })

  const ongsActives = computed(() => {
    return ongs.value.filter((o) => o.status === "ACTIVE")
  })

  const statistiques = computed(() => {
    const total = ongs.value.length
    const actives = ongsActives.value.length
    const enAttente = demandesONG.value.length
    const regionsCount = new Set(ongs.value.map((o) => o.region).filter(Boolean)).size

    return {
      totalONG: total,
      ongActives: actives,
      totalUtilisateurs: actives * 5,
      totalProjets: actives * 3,
      revenuMensuel: 0,
      tauxActivation: total > 0 ? Math.round((actives / total) * 100) : 0,
      abonnementsActifs: actives,
      abonnementsExpires: 0,
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
      const hasFile = payload.logo instanceof File
      const requestPayload = hasFile ? new FormData() : payload

      if (hasFile) {
        Object.entries(payload).forEach(([key, value]) => {
          if (value !== null && value !== "") requestPayload.append(key, value)
        })
      }

      const response = await api.post("/api/organizations/register/", requestPayload)
      await fetchAll().catch(() => {})
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
      await fetchAll().catch(() => {})
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
      await fetchAll().catch(() => {})
    } catch (e) {
      error.value = getErrorMessage(e)
      throw e
    } finally {
      loading.value = false
    }
  }

  return {
    ongs,
    demandesONG,
    ongsActives,
    statistiques,
    loading,
    error,
    formatMontant,
    fetchAll,
    createONG,
    approveONG,
    rejectONG,
  }
})


