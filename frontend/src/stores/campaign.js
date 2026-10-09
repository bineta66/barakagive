import { ref, computed } from "vue"
import { defineStore } from "pinia"
import api, { getErrorMessage } from "@/services/api.js"

export const useCampaignStore = defineStore("campaign", () => {
  const campaigns = ref([])
  const currentCampaign = ref(null)
  const agents = ref([])
  const loading = ref(false)
  const error = ref(null)
  const pagination = ref({ count: 0, next: null, previous: null })
  const campaignQuery = ref({ page: 1, page_size: 20 })
  let agentRequestId = 0

  const activeCampaigns = computed(() => {
    const today = new Date().toISOString().split("T")[0]
    return campaigns.value.filter(
      (c) => (!c.date_debut || c.date_debut <= today) && (!c.date_fin || c.date_fin >= today)
    )
  })

  const totalCampaigns = computed(() => pagination.value.count || campaigns.value.length)

  const fetchCampaigns = async (params = null) => {
    if (params) campaignQuery.value = { ...campaignQuery.value, ...params }
    loading.value = true
    error.value = null
    try {
      const response = await api.get("/api/campaigns/", { params: campaignQuery.value })
      const data = response.data
      campaigns.value = Array.isArray(data) ? data : (data.results || [])
      pagination.value = Array.isArray(data)
        ? { count: data.length, next: null, previous: null }
        : { count: data.count || 0, next: data.next || null, previous: data.previous || null }
      return campaigns.value
    } catch (err) {
      error.value = getErrorMessage(err)
      throw err
    } finally {
      loading.value = false
    }
  }

  const fetchAgentCampaigns = async (params = {}) => {
    loading.value = true
    error.value = null
    try {
      const response = await api.get("/api/agent/campagnes/", { params: { page: 1, page_size: 20, ...params } })
      const data = response.data
      campaigns.value = Array.isArray(data) ? data : (data.results || [])
      pagination.value = Array.isArray(data)
        ? { count: data.length, next: null, previous: null }
        : { count: data.count || 0, next: data.next || null, previous: data.previous || null }
      return campaigns.value
    } catch (err) {
      error.value = getErrorMessage(err)
      throw err
    } finally {
      loading.value = false
    }
  }

  const fetchCampaign = async (id) => {
    loading.value = true
    error.value = null
    try {
      const response = await api.get(`/api/campaigns/${id}/`)
      currentCampaign.value = response.data
      return response.data
    } catch (err) {
      error.value = getErrorMessage(err)
      throw err
    } finally {
      loading.value = false
    }
  }

  const fetchAgents = async (params = {}) => {
    const requestId = ++agentRequestId
    error.value = null
    try {
      const response = await api.get("/api/accounts/agents/", { params })
      const page = response.data?.results ? response.data : null
      const result = page?.results || response.data
      if (requestId === agentRequestId) agents.value = result
      return result
    } catch (err) {
      error.value = getErrorMessage(err)
      throw err
    }
  }

  const createCampaign = async (payload) => {
    loading.value = true
    error.value = null
    try {
      const response = await api.post("/api/campaigns/", payload)
      await fetchCampaigns().catch(() => {})
      return response.data
    } catch (err) {
      error.value = getErrorMessage(err)
      throw err
    } finally {
      loading.value = false
    }
  }

  const updateCampaign = async (id, payload) => {
    loading.value = true
    error.value = null
    try {
      const response = await api.patch(`/api/campaigns/${id}/`, payload)
      await fetchCampaigns().catch(() => {})
      return response.data
    } catch (err) {
      error.value = getErrorMessage(err)
      throw err
    } finally {
      loading.value = false
    }
  }

  const fetchCampaignAffectations = async (id) => {
    error.value = null
    try {
      const response = await api.get(`/api/campaigns/${id}/agents/zones/`)
      return response.data
    } catch (err) {
      error.value = getErrorMessage(err)
      throw err
    }
  }

  const assignAgentZones = async (id, payload) => {
    error.value = null
    try {
      const response = await api.put(`/api/campaigns/${id}/agents/zones/`, payload)
      return response.data
    } catch (err) {
      error.value = getErrorMessage(err)
      throw err
    }
  }

  const deleteCampaign = async (id) => {
    loading.value = true
    error.value = null
    try {
      await api.delete(`/api/campaigns/${id}/`)
      await fetchCampaigns().catch(() => {})
    } catch (err) {
      error.value = getErrorMessage(err)
      throw err
    } finally {
      loading.value = false
    }
  }

  return {
    campaigns,
    pagination,
    campaignQuery,
    currentCampaign,
    agents,
    loading,
    error,
    activeCampaigns,
    totalCampaigns,
    fetchCampaigns,
    fetchAgentCampaigns,
    fetchAgents,
    fetchCampaign,
    createCampaign,
    updateCampaign,
    deleteCampaign,
    fetchCampaignAffectations,
    assignAgentZones,
  }
})
