import { ref, computed } from "vue"
import { defineStore } from "pinia"
import api, { getErrorMessage } from "@/services/api.js"

export const useOrganizationStore = defineStore("organization", () => {
  const organizations = ref([])
  const currentOrganization = ref(null)
  const loading = ref(false)
  const error = ref(null)

  const totalOrganizations = computed(() => organizations.value.length)
  const activeOrganizations = computed(
    () => organizations.value.filter((o) => o.status === "ACTIVE").length
  )
  const pendingOrganizations = computed(
    () => organizations.value.filter((o) => o.status === "PENDING").length
  )

  const fetchOrganizations = async () => {
    loading.value = true
    error.value = null
    try {
      const response = await api.get("/api/organizations/")
      organizations.value = response.data
      return response.data
    } catch (err) {
      error.value = getErrorMessage(err)
      throw err
    } finally {
      loading.value = false
    }
  }

  const registerOrganization = async (payload) => {
    loading.value = true
    error.value = null
    try {
      const response = await api.post("/api/organizations/register/", payload)
      await fetchOrganizations().catch(() => {})
      return response.data
    } catch (err) {
      error.value = getErrorMessage(err)
      throw err
    } finally {
      loading.value = false
    }
  }

  return {
    organizations,
    currentOrganization,
    loading,
    error,
    totalOrganizations,
    activeOrganizations,
    pendingOrganizations,
    fetchOrganizations,
    registerOrganization,
  }
})
