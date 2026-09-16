import { ref, computed } from "vue"
import { defineStore } from "pinia"
import api, { getErrorMessage } from "@/services/api.js"

export const useProjectStore = defineStore("project", () => {
  const projects = ref([])
  const currentProject = ref(null)
  const criteria = ref([])
  const loading = ref(false)
  const error = ref(null)

  const activeProjects = computed(() => projects.value.filter((p) => !p.archived))
  const archivedProjects = computed(() => projects.value.filter((p) => p.archived))
  const totalBudget = computed(() => {
    return activeProjects.value.reduce((acc, p) => acc + (parseFloat(p.budget) || 0), 0)
  })

  const fetchProjects = async () => {
    loading.value = true
    error.value = null
    try {
      const response = await api.get("/api/projects/")
      projects.value = response.data
      return response.data
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

  const fetchCriteria = async () => {
    try {
      const response = await api.get("/api/project-criteria/")
      criteria.value = response.data
      return response.data
    } catch (err) {
      error.value = getErrorMessage(err)
      return []
    }
  }

  const createCriteria = async (name) => {
    try {
      const response = await api.post("/api/project-criteria/", { name })
      await fetchCriteria()
      return response.data
    } catch (err) {
      error.value = getErrorMessage(err)
      throw err
    }
  }

  return {
    projects,
    currentProject,
    criteria,
    loading,
    error,
    activeProjects,
    archivedProjects,
    totalBudget,
    fetchProjects,
    fetchProject,
    createProject,
    updateProject,
    archiveProject,
    fetchCriteria,
    createCriteria,
  }
})
