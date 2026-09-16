import { ref, computed } from "vue"
import { defineStore } from "pinia"
import api, { getErrorMessage } from "@/services/api.js"

export const useFormStore = defineStore("form", () => {
  const forms = ref([])
  const currentForm = ref(null)
  const loading = ref(false)
  const error = ref(null)

  const publishedForms = computed(() => forms.value.filter((f) => f.statut === "PUBLIE"))
  const draftForms = computed(() => forms.value.filter((f) => f.statut === "BROUILLON"))

  const fetchForms = async () => {
    loading.value = true
    error.value = null
    try {
      const response = await api.get("/api/forms/")
      forms.value = response.data
      return response.data
    } catch (err) {
      error.value = getErrorMessage(err)
      throw err
    } finally {
      loading.value = false
    }
  }

  const fetchForm = async (id) => {
    loading.value = true
    error.value = null
    try {
      const response = await api.get(`/api/forms/${id}/`)
      currentForm.value = response.data
      return response.data
    } catch (err) {
      error.value = getErrorMessage(err)
      throw err
    } finally {
      loading.value = false
    }
  }

  const createForm = async (payload) => {
    loading.value = true
    error.value = null
    try {
      const response = await api.post("/api/forms/", payload)
      currentForm.value = response.data
      await fetchForms().catch(() => {})
      return response.data
    } catch (err) {
      error.value = getErrorMessage(err)
      throw err
    } finally {
      loading.value = false
    }
  }

  const updateForm = async (id, payload) => {
    loading.value = true
    error.value = null
    try {
      const response = await api.patch(`/api/forms/${id}/`, payload)
      currentForm.value = response.data
      await fetchForms().catch(() => {})
      return response.data
    } catch (err) {
      error.value = getErrorMessage(err)
      throw err
    } finally {
      loading.value = false
    }
  }

  const deleteForm = async (id) => {
    loading.value = true
    error.value = null
    try {
      await api.delete(`/api/forms/${id}/`)
      if (currentForm.value?.id === id) currentForm.value = null
      await fetchForms().catch(() => {})
    } catch (err) {
      error.value = getErrorMessage(err)
      throw err
    } finally {
      loading.value = false
    }
  }

  const publishForm = async (id) => {
    loading.value = true
    error.value = null
    try {
      const response = await api.patch(`/api/forms/${id}/publish/`)
      await fetchForm(id).catch(() => {})
      await fetchForms().catch(() => {})
      return response.data
    } catch (err) {
      error.value = getErrorMessage(err)
      throw err
    } finally {
      loading.value = false
    }
  }

  const addQuestion = async (formId, questionData) => {
    loading.value = true
    error.value = null
    try {
      const response = await api.post(`/api/forms/${formId}/questions/`, questionData)
      await fetchForm(formId).catch(() => {})
      return response.data
    } catch (err) {
      error.value = getErrorMessage(err)
      throw err
    } finally {
      loading.value = false
    }
  }

  const updateQuestion = async (questionId, questionData) => {
    loading.value = true
    error.value = null
    try {
      const response = await api.patch(`/api/forms/questions/${questionId}/`, questionData)
      if (currentForm.value?.id) {
        await fetchForm(currentForm.value.id).catch(() => {})
      }
      return response.data
    } catch (err) {
      error.value = getErrorMessage(err)
      throw err
    } finally {
      loading.value = false
    }
  }

  const deleteQuestion = async (questionId) => {
    loading.value = true
    error.value = null
    try {
      await api.delete(`/api/forms/questions/${questionId}/`)
      if (currentForm.value?.id) {
        await fetchForm(currentForm.value.id).catch(() => {})
      }
    } catch (err) {
      error.value = getErrorMessage(err)
      throw err
    } finally {
      loading.value = false
    }
  }

  const duplicateQuestion = async (questionId) => {
    loading.value = true
    error.value = null
    try {
      const response = await api.post(`/api/forms/questions/${questionId}/duplicate/`)
      if (currentForm.value?.id) {
        await fetchForm(currentForm.value.id).catch(() => {})
      }
      return response.data
    } catch (err) {
      error.value = getErrorMessage(err)
      throw err
    } finally {
      loading.value = false
    }
  }

  const reorderQuestions = async (formulaireId, questionsList) => {
    loading.value = true
    error.value = null
    try {
      const response = await api.patch("/api/forms/questions/reorder/", {
        formulaire_id: formulaireId,
        questions: questionsList,
      })
      if (currentForm.value?.id) {
        await fetchForm(currentForm.value.id).catch(() => {})
      }
      return response.data
    } catch (err) {
      error.value = getErrorMessage(err)
      throw err
    } finally {
      loading.value = false
    }
  }

  return {
    forms,
    currentForm,
    loading,
    error,
    publishedForms,
    draftForms,
    fetchForms,
    fetchForm,
    createForm,
    updateForm,
    deleteForm,
    publishForm,
    addQuestion,
    updateQuestion,
    deleteQuestion,
    duplicateQuestion,
    reorderQuestions,
  }
})
