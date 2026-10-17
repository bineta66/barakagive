import { ref, computed } from "vue"
import { defineStore } from "pinia"
import api, { getErrorMessage } from "@/services/api.js"

export const useZoneStore = defineStore("zone", () => {
  const zones = ref([])
  const currentZone = ref(null)
  const loading = ref(false)
  const error = ref(null)

  const activeZones = computed(() => zones.value.filter((z) => z.statut))
  const totalZones = computed(() => zones.value.length)

  const fetchZones = async () => {
    loading.value = true
    error.value = null
    try {
      const response = await api.get("/api/zones/")
      zones.value = response.data
      return response.data
    } catch (err) {
      error.value = getErrorMessage(err)
      throw err
    } finally {
      loading.value = false
    }
  }

  const fetchZone = async (id) => {
    loading.value = true
    error.value = null
    try {
      const response = await api.get(`/api/zones/${id}/`)
      currentZone.value = response.data
      return response.data
    } catch (err) {
      error.value = getErrorMessage(err)
      throw err
    } finally {
      loading.value = false
    }
  }

  const createZone = async (payload) => {
    loading.value = true
    error.value = null
    try {
      const response = await api.post("/api/zones/", payload)
      await fetchZones().catch(() => {})
      return response.data
    } catch (err) {
      error.value = getErrorMessage(err)
      throw err
    } finally {
      loading.value = false
    }
  }

  const updateZone = async (id, payload) => {
    loading.value = true
    error.value = null
    try {
      const response = await api.patch(`/api/zones/${id}/`, payload)
      await fetchZones().catch(() => {})
      return response.data
    } catch (err) {
      error.value = getErrorMessage(err)
      throw err
    } finally {
      loading.value = false
    }
  }

  const deleteZone = async (id) => {
    loading.value = true
    error.value = null
    try {
      await api.delete(`/api/zones/${id}/`)
      await fetchZones().catch(() => {})
    } catch (err) {
      error.value = getErrorMessage(err)
      throw err
    } finally {
      loading.value = false
    }
  }

  const reverseGeocode = async (latitude, longitude) => {
    try {
      const response = await api.post("/api/zones/reverse-geocode/", {
        latitude: parseFloat(latitude),
        longitude: parseFloat(longitude),
      })
      return response.data
    } catch (err) {
      error.value = getErrorMessage(err)
      return null
    }
  }

  return {
    zones,
    currentZone,
    loading,
    error,
    activeZones,
    totalZones,
    fetchZones,
    fetchZone,
    createZone,
    updateZone,
    deleteZone,
    reverseGeocode,
  }
})
