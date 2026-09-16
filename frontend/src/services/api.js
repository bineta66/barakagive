import axios from "axios"

const baseURL = import.meta.env.VITE_API_URL || ""

const api = axios.create({
  baseURL,
  headers: {
    "Content-Type": "application/json",
  },
})

let isRefreshing = false
let failedQueue = []

const processQueue = (error, token = null) => {
  failedQueue.forEach((prom) => {
    if (error) {
      prom.reject(error)
    } else {
      prom.resolve(token)
    }
  })
  failedQueue = []
}

// Request Interceptor: Attach JWT Access Token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem("accessToken")
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => Promise.reject(error)
)

// Response Interceptor: Handle 401 and Auto-refresh
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config

    if (!originalRequest) {
      return Promise.reject(error)
    }

    // Do not attempt refresh on auth endpoints
    const isAuthEndpoint =
      originalRequest.url?.includes("/api/accounts/login/") ||
      originalRequest.url?.includes("/api/token/") ||
      originalRequest.url?.includes("/api/accounts/refresh/") ||
      originalRequest.url?.includes("/api/accounts/activate/")

    if (error.response?.status === 401 && !originalRequest._retry && !isAuthEndpoint) {
      if (isRefreshing) {
        return new Promise((resolve, reject) => {
          failedQueue.push({ resolve, reject })
        })
          .then((token) => {
            originalRequest.headers.Authorization = `Bearer ${token}`
            return api(originalRequest)
          })
          .catch((err) => Promise.reject(err))
      }

      originalRequest._retry = true
      isRefreshing = true

      const refreshToken = localStorage.getItem("refreshToken")
      if (!refreshToken) {
        processQueue(new Error("No refresh token available"), null)
        isRefreshing = false
        localStorage.removeItem("accessToken")
        localStorage.removeItem("refreshToken")
        localStorage.removeItem("user")
        if (typeof window !== "undefined" && window.location.pathname !== "/connexion") {
          window.location.href = "/connexion"
        }
        return Promise.reject(error)
      }

      try {
        const refreshUrl = `${baseURL}/api/accounts/refresh/`
        const response = await axios.post(refreshUrl, { refresh: refreshToken })
        const newAccessToken = response.data.access
        const newRefreshToken = response.data.refresh || refreshToken

        localStorage.setItem("accessToken", newAccessToken)
        localStorage.setItem("refreshToken", newRefreshToken)

        api.defaults.headers.common.Authorization = `Bearer ${newAccessToken}`
        originalRequest.headers.Authorization = `Bearer ${newAccessToken}`

        processQueue(null, newAccessToken)
        return api(originalRequest)
      } catch (refreshError) {
        processQueue(refreshError, null)
        localStorage.removeItem("accessToken")
        localStorage.removeItem("refreshToken")
        localStorage.removeItem("user")
        if (typeof window !== "undefined" && window.location.pathname !== "/connexion") {
          window.location.href = "/connexion"
        }
        return Promise.reject(refreshError)
      } finally {
        isRefreshing = false
      }
    }

    return Promise.reject(error)
  }
)

/**
 * Helper to extract human-readable error messages from DRF error responses.
 */
export const getErrorMessage = (error) => {
  if (!error) return "Une erreur inattendue est survenue."

  if (error.response?.data) {
    const data = error.response.data

    if (typeof data === "string") return data

    if (data.detail) {
      if (Array.isArray(data.detail)) return data.detail.join(" ")
      return String(data.detail)
    }

    if (data.message) return String(data.message)

    if (typeof data === "object") {
      const messages = []
      for (const [key, value] of Object.entries(data)) {
        const fieldName = key === "non_field_errors" ? "" : `${key}: `
        if (Array.isArray(value)) {
          messages.push(`${fieldName}${value.join(" ")}`)
        } else if (typeof value === "object" && value !== null) {
          messages.push(`${fieldName}${JSON.stringify(value)}`)
        } else {
          messages.push(`${fieldName}${value}`)
        }
      }
      if (messages.length > 0) return messages.join(" | ")
    }
  }

  if (error.message) return error.message
  return "Une erreur est survenue lors de la communication avec le serveur."
}

export default api
