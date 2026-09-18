import { ref, computed } from "vue"
import { defineStore } from "pinia"
import api, { getErrorMessage } from "@/services/api.js"

export const ROLES = {
  SUPER_ADMIN: "SUPER_ADMIN",
  GERANT: "GERANT",
  CHEF_PROJET: "CHEF_PROJET",
  FINANCE: "FINANCE",
  AGENT: "AGENT",
}

export const useAuthStore = defineStore("auth", () => {
  const getStoredUser = () => {
    try {
      const u = localStorage.getItem("user")
      return u ? JSON.parse(u) : null
    } catch {
      return null
    }
  }

  const user = ref(getStoredUser())
  const accessToken = ref(localStorage.getItem("accessToken") || null)
  const refreshToken = ref(localStorage.getItem("refreshToken") || null)
  const loading = ref(false)
  const error = ref(null)

  const isAuthenticated = computed(() => !!accessToken.value)
  const role = computed(() => user.value?.role || null)
  const isGerant = computed(() => user.value?.role === "GERANT")
  const isFinance = computed(() => user.value?.role === "FINANCE")
  const isChefProjet = computed(() => user.value?.role === "CHEF_PROJET")
  const isSuperAdmin = computed(() => user.value?.role === "SUPER_ADMIN")
  const isAgent = computed(() => user.value?.role === "AGENT")
  const nom = computed(() => {
    if (!user.value) return ""
    if (user.value.full_name) return user.value.full_name
    return `${user.value.first_name || ""} ${user.value.last_name || ""}`.trim()
  })
  const email = computed(() => user.value?.email || "")
  const organizationId = computed(() => user.value?.organization || null)

  const setAuthData = (data) => {
    accessToken.value = data.access
    refreshToken.value = data.refresh
    user.value = data.user

    localStorage.setItem("accessToken", data.access)
    localStorage.setItem("refreshToken", data.refresh)
    localStorage.setItem("user", JSON.stringify(data.user))
  }

  const clearAuthData = () => {
    accessToken.value = null
    refreshToken.value = null
    user.value = null
    localStorage.removeItem("accessToken")
    localStorage.removeItem("refreshToken")
    localStorage.removeItem("user")
  }

  const login = async (loginEmail, password) => {
    loading.value = true
    error.value = null
    try {
      const response = await api.post("/api/accounts/login/", {
        email: loginEmail,
        password,
      })
      setAuthData(response.data)
      return response.data.user
    } catch (err) {
      error.value = getErrorMessage(err)
      throw err
    } finally {
      loading.value = false
    }
  }

  const logout = async () => {
    loading.value = true
    try {
      if (refreshToken.value) {
        await api.post("/api/accounts/logout/", { refresh: refreshToken.value }).catch(() => {})
      }
    } finally {
      clearAuthData()
      loading.value = false
    }
  }

  const fetchMe = async () => {
    if (!accessToken.value) return null
    try {
      const response = await api.get("/api/accounts/me/")
      user.value = response.data
      localStorage.setItem("user", JSON.stringify(response.data))
      return response.data
    } catch (err) {
      if (err.response?.status === 401) {
        clearAuthData()
      }
      throw err
    }
  }

  const activateAccount = async (token, password, passwordConfirm) => {
    loading.value = true
    error.value = null
    try {
      const response = await api.post("/api/accounts/activate/", {
        token,
        password,
        password_confirm: passwordConfirm,
      })
      return response.data
    } catch (err) {
      error.value = getErrorMessage(err)
      throw err
    } finally {
      loading.value = false
    }
  }

  const getDefaultRouteForRole = (userRole) => {
    switch (userRole) {
      case ROLES.SUPER_ADMIN:
        return "/super-admin/dashboard"
      case ROLES.GERANT:
        return "/gerant/dashboard"
      case ROLES.CHEF_PROJET:
        return "/chef-projet/dashboard"
      case ROLES.AGENT:
          return "/agent/campagnes"
      case ROLES.FINANCE:
        return "/finance/dashboard"
      default:
        return "/connexion"
    }
  }

  return {
    user,
    accessToken,
    refreshToken,
    loading,
    error,
    isAuthenticated,
    role,
    isGerant,
    isFinance,
    isChefProjet,
    isSuperAdmin,
    isAgent,
    nom,
    email,
    organizationId,
    login,
    logout,
    fetchMe,
    activateAccount,
    getDefaultRouteForRole,
  }
})
