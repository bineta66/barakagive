import { ref, computed, watch } from "vue"
import { defineStore } from "pinia"
import api from "@/services/api.js"
import { useAuthStore } from "@/stores/auth.js"
import { clearAssistantHistoryStorage, redactHistoryText } from "@/services/assistantHistory.js"

const STORAGE_PREFIX = "barakagive_finance_assistant_history"
const MAX_STORED = 80
const AUDIO_DB = "BarakaGiveFinanceVoice"
const AUDIO_STORE = "voice_attachments"

function openAudioDb() {
  return new Promise((resolve, reject) => {
    const request = indexedDB.open(AUDIO_DB, 1)
    request.onupgradeneeded = () => request.result.createObjectStore(AUDIO_STORE, { keyPath: "id" })
    request.onsuccess = () => resolve(request.result)
    request.onerror = () => reject(request.error)
  })
}

async function audioRequest(mode, operation) {
  const db = await openAudioDb()
  return new Promise((resolve, reject) => {
    const tx = db.transaction(AUDIO_STORE, mode)
    const request = operation(tx.objectStore(AUDIO_STORE))
    request.onsuccess = () => resolve(request.result)
    request.onerror = () => reject(request.error)
    tx.oncomplete = () => db.close()
    tx.onerror = () => { db.close(); reject(tx.error) }
  })
}

function loadHistory(storageKey) {
  try {
    const raw = localStorage.getItem(storageKey)
    return raw ? JSON.parse(raw).map(message => ({ ...message, audioUrl: "" })) : []
  } catch {
    return []
  }
}

function saveHistory(msgs, storageKey) {
  try {
    localStorage.setItem(
      storageKey,
      JSON.stringify(msgs.filter(m => !m.loading).slice(-MAX_STORED).map(({ audioUrl, ...message }) => ({
        ...message,
        content: redactHistoryText(message.content),
      })))
    )
  } catch { /* mode privé */ }
}

export const useFinanceAssistantStore = defineStore("financeAssistant", () => {
  const authStore = useAuthStore()
  const identityKey = () => `${authStore.user?.organization || "no-org"}:${authStore.user?.id || authStore.user?.email || "anonymous"}`
  const activeIdentity = ref(identityKey())
  const storageKey = () => `${STORAGE_PREFIX}:${activeIdentity.value}`

  // ── State ────────────────────────────────────────────────────────────
  const messages = ref(loadHistory(storageKey()))
  const isLoading = ref(false)
  const loadingHome = ref(false)
  const error = ref(null)
  const isOpen = ref(false)
  const alertLevel = ref("GREEN")   // GREEN | YELLOW | ORANGE | RED
  const homeData = ref(null)

  // Suggestions rapides spécialisées finance selon le prompt
  const quickSuggestions = [
    {
      id: 1,
      title: "Raison de l'alerte",
      text: "Pourquoi l'alerte est Orange ?",
      icon: "pi pi-exclamation-triangle",
    },
    {
      id: 2,
      title: "Plus grand dépenseur",
      text: "Quel projet dépense le plus ?",
      icon: "pi pi-chart-line",
    },
    {
      id: 3,
      title: "Solde budgétaire",
      text: "Combien reste-t-il dans le budget ?",
      icon: "pi pi-wallet",
    },
    {
      id: 4,
      title: "Consommation par région",
      text: "Quelle région consomme le plus ?",
      icon: "pi pi-map-marker",
    },
    {
      id: 5,
      title: "Incohérences",
      text: "Quelles dépenses sont incohérentes ?",
      icon: "pi pi-shield",
    },
    {
      id: 6,
      title: "Pièces justificatives",
      text: "Quels justificatifs sont à vérifier ?",
      icon: "pi pi-file-check",
    },
  ]

  // ── Persistance ──────────────────────────────────────────────────────
  watch(messages, (msgs) => saveHistory(msgs, storageKey()), { deep: true })
  watch(identityKey, (identity, previous) => {
    if (identity !== previous) {
      activeIdentity.value = identity
      clearAssistantHistoryStorage()
      messages.value = []
    }
  })

  // ── Getters ──────────────────────────────────────────────────────────
  const hasMessages = computed(() => messages.value.length > 0)
  const lastMessage = computed(() => messages.value[messages.value.length - 1] ?? null)

  // Couleurs CSS dynamiques selon le niveau d'alerte
  const alertColors = computed(() => {
    switch (alertLevel.value) {
      case "RED": return { orb: "bg-rose-baraka", ring: "border-rose-baraka/70", text: "text-rose-baraka", badge: "bg-rose-baraka" }
      case "ORANGE": return { orb: "bg-rose-baraka/80", ring: "border-rose-baraka/50", text: "text-rose-baraka", badge: "bg-rose-baraka/80" }
      case "YELLOW": return { orb: "bg-bleu-accent", ring: "border-bleu-accent/70", text: "text-bleu-accent", badge: "bg-bleu-accent" }
      default: return { orb: "bg-bleu-accent", ring: "border-bleu-accent/70", text: "text-bleu-accent", badge: "bg-bleu-accent" }
    }
  })

  // ── Actions ──────────────────────────────────────────────────────────
  const toggleAssistant = () => {
    isOpen.value = !isOpen.value
    if (isOpen.value) {
      fetchHomeData()
    }
  }

  const openAssistant = () => {
    isOpen.value = true
    fetchHomeData()
  }

  const closeAssistant = () => {
    isOpen.value = false
  }

  const clearHistory = () => {
    const voiceIds = messages.value.map(message => message.audioId).filter(Boolean)
    messages.value = []
    error.value = null
    alertLevel.value = "GREEN"
    localStorage.removeItem(storageKey())
    if (voiceIds.length && typeof indexedDB !== "undefined") {
      void openAudioDb().then(db => {
        const tx = db.transaction(AUDIO_STORE, "readwrite")
        voiceIds.forEach(id => tx.objectStore(AUDIO_STORE).delete(id))
        tx.oncomplete = () => db.close()
      }).catch(() => {})
    }
  }

  const saveVoiceAttachment = async blob => {
    if (!blob || typeof indexedDB === "undefined") return ""
    const currentOwner = identityKey()
    const id = `${currentOwner}-${Date.now()}-${Math.random().toString(36).slice(2, 8)}`
    try {
      await audioRequest("readwrite", store => store.put({ id, owner: currentOwner, blob, createdAt: Date.now() }))
      const all = await audioRequest("readonly", store => store.getAll())
      const mine = all.filter(item => item.owner === currentOwner).sort((a, b) => b.createdAt - a.createdAt)
      const removeIds = mine.slice(20).map(item => item.id)
      if (removeIds.length) await audioRequest("readwrite", store => { removeIds.forEach(value => store.delete(value)); return store.get(id) })
      return id
    } catch {
      return ""
    }
  }

  const restoreVoiceAttachments = async () => {
    if (typeof indexedDB === "undefined") return
    for (const message of messages.value) {
      if (!message.audioId || message.audioUrl) continue
      try {
        const item = await audioRequest("readonly", store => store.get(message.audioId))
        if (item?.owner === identityKey() && item.blob) message.audioUrl = URL.createObjectURL(item.blob)
      } catch { /* L'historique texte reste disponible si le stockage audio est indisponible. */ }
    }
  }
  void restoreVoiceAttachments()

  // Récupérer les données de la détection automatique (GET /api/finance/assistant/home)
  const fetchHomeData = async () => {
    loadingHome.value = true
    try {
      const res = await api.get("/api/finance/assistant/home/")
      homeData.value = res.data
      // Toujours mettre à jour l'alerte — même si GREEN
      if (res.data?.alert && ["GREEN", "YELLOW", "ORANGE", "RED"].includes(res.data.alert)) {
        alertLevel.value = res.data.alert
      } else {
        alertLevel.value = "GREEN"
      }
      return res.data
    } catch (err) {
      console.warn("Impossible de charger /api/finance/assistant/home", err)
      fetchAlertStatus()
    } finally {
      loadingHome.value = false
    }
  }

  const _push = (role, content, extra = {}) => {
    const msg = {
      id: `${role}-${Date.now()}-${Math.random().toString(36).slice(2, 6)}`,
      role,
      content,
      timestamp: new Date().toISOString(),
      ...extra,
    }
    messages.value.push(msg)
    return msg
  }

  const sendMessage = async (question, pageContext = null, voice = null) => {
    if (!question?.trim() || isLoading.value) return false

    error.value = null
    const audioId = voice?.blob ? await saveVoiceAttachment(voice.blob) : ""
    const audioUrl = voice?.blob ? URL.createObjectURL(voice.blob) : ""
    _push("user", question.trim(), {
      isVoice: Boolean(voice?.blob), audioId, audioUrl,
      durationSeconds: Number(voice?.durationSeconds || 0),
    })
    const placeholder = _push("assistant", "", {
      loading: true,
      voiceResponse: Boolean(voice?.blob),
    })
    isLoading.value = true

    try {
      const res = await api.post("/api/finance/assistant/chat/", {
        question: question.trim(),
        page_context: pageContext,
      })

      // Ne pas changer alertLevel depuis le chat — seul fetchHomeData fait autorité
      // if (res.data?.alert ...) { alertLevel.value = ... }

      // Extraire la réponse — gérer tous les formats possibles
      let answer = ""
      const d = res.data
      if (typeof d === "string") {
        // Réponse brute string
        answer = d
      } else if (d?.answer && typeof d.answer === "string") {
        answer = d.answer
      } else if (d?.answer && typeof d.answer === "object") {
        // Parfois l'IA retourne un objet JSON avec answer imbriqué
        answer = d.answer?.answer || JSON.stringify(d.answer)
      } else if (d?.response && typeof d.response === "string") {
        answer = d.response
      } else if (d?.content && typeof d.content === "string") {
        answer = d.content
      } else if (d?.text && typeof d.text === "string") {
        answer = d.text
      } else if (typeof d === "object") {
        // Essayer de parser si c'est du JSON brut dans la string
        try {
          const str = JSON.stringify(d)
          answer = str !== "{}" ? str : "Je n'ai pas pu générer une réponse. Veuillez réessayer."
        } catch {
          answer = "Je n'ai pas pu générer une réponse. Veuillez réessayer."
        }
      } else {
        answer = "Je n'ai pas pu générer une réponse. Veuillez réessayer."
      }


      const idx = messages.value.findIndex(m => m.id === placeholder.id)
      if (idx !== -1) {
        messages.value[idx] = {
          ...messages.value[idx],
          content: answer,
          alert: res.data?.alert ?? alertLevel.value,
          timestamp: res.data?.generated_at ?? new Date().toISOString(),
          loading: false,
        }
      }
      return true
    } catch (err) {
      // S'assurer que errMsg est toujours une string
      const rawErr = err.response?.data?.detail ?? err.response?.data?.answer ?? err.response?.data ?? null
      const errMsg = rawErr
        ? (typeof rawErr === "string" ? rawErr : JSON.stringify(rawErr))
        : "Le service IA Finance est momentanément indisponible."

      const idx = messages.value.findIndex(m => m.id === placeholder.id)
      if (idx !== -1) {
        messages.value[idx] = {
          ...messages.value[idx],
          content: errMsg,
          loading: false,
          isError: true,
          // Ne pas changer le niveau d'alerte en cas d'erreur réseau
          alert: alertLevel.value,
        }
      }
      error.value = errMsg
      return false
    } finally {
      isLoading.value = false
    }
  }

  const fetchAlertStatus = async () => {
    try {
      const res = await api.get("/api/finance/assistant/home/")
      if (res.data?.alert) {
        alertLevel.value = res.data.alert
        homeData.value = res.data
      }
    } catch {
      try {
        const res = await api.get("/api/finance/dashboard/")
        const data = res.data
        if (data) {
          const bt = data.budget_total || 0
          const solde = data.solde || 0
          const taux = data.taux_execution || 0

          if (taux >= 90 || (bt > 0 && solde / bt < 0.05)) {
            alertLevel.value = "RED"
          } else if (taux >= 75 || (bt > 0 && solde / bt < 0.15)) {
            alertLevel.value = "ORANGE"
          } else if (taux >= 50 || (bt > 0 && solde / bt < 0.30)) {
            alertLevel.value = "YELLOW"
          } else {
            alertLevel.value = "GREEN"
          }
        }
      } catch { /* Silent */ }
    }
  }

  return {
    messages,
    isLoading,
    loadingHome,
    error,
    isOpen,
    alertLevel,
    homeData,
    alertColors,
    quickSuggestions,
    hasMessages,
    lastMessage,
    toggleAssistant,
    openAssistant,
    closeAssistant,
    clearHistory,
    fetchHomeData,
    sendMessage,
    fetchAlertStatus,
    restoreVoiceAttachments,
  }
})
