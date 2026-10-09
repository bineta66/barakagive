import { ref, computed } from "vue"
import { defineStore } from "pinia"
import api, { getErrorMessage } from "@/services/api.js"

export const useProjectStore = defineStore("project", () => {
  const projects = ref([])
  const currentProject = ref(null)
  const criteria = ref([])
  const decisionDashboard = ref(null)
  const loading = ref(false)
  const error = ref(null)
  const pagination = ref({ count: 0, next: null, previous: null })
  const projectQuery = ref({ page: 1, page_size: 20 })

  const activeProjects = computed(() => projects.value.filter((p) => !p.archived))
  const archivedProjects = computed(() => projects.value.filter((p) => p.archived))
  const totalBudget = computed(() => {
    return activeProjects.value.reduce((acc, p) => acc + (parseFloat(p.budget) || 0), 0)
  })

  const fetchProjects = async (params = null) => {
    if (params) projectQuery.value = { ...projectQuery.value, ...params }
    loading.value = true
    error.value = null
    try {
      const response = await api.get("/api/projects/", { params: projectQuery.value })
      const data = response.data
      projects.value = data?.results ?? (Array.isArray(data) ? data : [])
      pagination.value = Array.isArray(data)
        ? { count: data.length, next: null, previous: null }
        : { count: data?.count || 0, next: data?.next || null, previous: data?.previous || null }
      return projects.value
    } catch (err) {
      error.value = getErrorMessage(err)
      throw err
    } finally {
      loading.value = false
    }
  }

  const fetchProject = async (id) => {
    loading.value = true
    error.value = null
    try {
      const response = await api.get(`/api/projects/${id}/`)
      currentProject.value = response.data
      return response.data
    } catch (err) {
      error.value = getErrorMessage(err)
      throw err
    } finally {
      loading.value = false
    }
  }

  const fetchDecisionDashboard = async (params = {}) => {
    try {
      const response = await api.get("/api/projects/dashboard/", { params })
      decisionDashboard.value = response.data
      return response.data
    } catch (err) {
      error.value = getErrorMessage(err)
      throw err
    }
  }

  const createProject = async (payload) => {
    loading.value = true
    error.value = null
    try {
      const response = await api.post("/api/projects/", payload)
      await fetchProjects().catch(() => {})
      return response.data
    } catch (err) {
      error.value = getErrorMessage(err)
      throw err
    } finally {
      loading.value = false
    }
  }

  const updateProject = async (id, payload) => {
    loading.value = true
    error.value = null
    try {
      const response = await api.patch(`/api/projects/${id}/`, payload)
      await fetchProjects().catch(() => {})
      return response.data
    } catch (err) {
      error.value = getErrorMessage(err)
      throw err
    } finally {
      loading.value = false
    }
  }

  const archiveProject = async (id) => {
    loading.value = true
    error.value = null
    try {
      await api.delete(`/api/projects/${id}/`)
      await fetchProjects().catch(() => {})
    } catch (err) {
      error.value = getErrorMessage(err)
      throw err
    } finally {
      loading.value = false
    }
  }

  const deleteProject = async (id) => {
    loading.value = true
    error.value = null
    try {
      await api.delete(`/api/projects/${id}/`)
      await fetchProjects().catch(() => {})
    } catch (err) {
      error.value = getErrorMessage(err)
      throw err
    } finally {
      loading.value = false
    }
  }

  const fetchCriteria = async (projectId) => {
    try {
      const response = await api.get(`/api/projets/${projectId}/criteres/`)
      criteria.value = response.data.criteres || []
      return response.data
    } catch (err) {
      error.value = getErrorMessage(err)
      return { criteres: [], total_poids: 0 }
    }
  }

  const createCriteria = async (projectId, data) => {
    try {
      const response = await api.post(`/api/projets/${projectId}/criteres/`, data)
      return response.data
    } catch (err) {
      error.value = getErrorMessage(err)
      throw err
    }
  }

  const updateCriteria = async (id, data) => {
    try {
      const response = await api.put(`/api/criteres/${id}/`, data)
      return response.data
    } catch (err) {
      error.value = getErrorMessage(err)
      throw err
    }
  }

  const deleteCriteria = async (id) => {
    try {
      await api.delete(`/api/criteres/${id}/`)
    } catch (err) {
      error.value = getErrorMessage(err)
      throw err
    }
  }

  return {
    projects,
    pagination,
    projectQuery,
    currentProject,
    criteria,
    decisionDashboard,
    loading,
    error,
    activeProjects,
    archivedProjects,
    totalBudget,
    fetchProjects,
    fetchProject,
    fetchDecisionDashboard,
    createProject,
    updateProject,
    archiveProject,
    deleteProject,
    fetchCriteria,
    createCriteria,
    updateCriteria,
    deleteCriteria,
  }
})
