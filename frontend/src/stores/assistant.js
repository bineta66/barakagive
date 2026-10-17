import { ref, computed, watch } from "vue"
import { defineStore } from "pinia"
import api from "@/services/api.js"
import { useAuthStore } from "@/stores/auth.js"
import { assistantIdentityKey, clearAssistantHistoryStorage, clearLegacyAssistantHistory, redactHistoryText } from "@/services/assistantHistory.js"

const STORAGE_PREFIX = "barakagive_assistant_history"
const SESSION_PREFIX = "barakagive_assistant_session"
const MAX_STORED = 100  // messages max gardés en localStorage
const AUDIO_DB_NAME = "BarakaGiveAssistantAudio"
const AUDIO_DB_VERSION = 1
const AUDIO_STORE_NAME = "voice_attachments"
const MAX_STORED_AUDIO = 20
clearLegacyAssistantHistory()

function saveHistory(msgs, storageKey) {
  try {
    // Ne persiste que les messages complets (pas les placeholders loading)
    const toSave = msgs
      .filter(m => !m.loading)
      .slice(-MAX_STORED)
      .map(({ audioUrl, audioUnavailable, ...message }) => ({
        ...message,
        content: redactHistoryText(message.content),
        ...(message.transcription ? { transcription: redactHistoryText(message.transcription) } : {}),
      }))
    localStorage.setItem(storageKey, JSON.stringify(toSave))
    void pruneVoiceAttachments()
  } catch {
    // Silently fail (e.g. private mode quota)
  }
}

function openVoiceDb() {
  return new Promise((resolve, reject) => {
    if (!globalThis.indexedDB) return reject(new Error("IndexedDB unavailable"))
    const request = indexedDB.open(AUDIO_DB_NAME, AUDIO_DB_VERSION)
    request.onupgradeneeded = () => {
      if (!request.result.objectStoreNames.contains(AUDIO_STORE_NAME)) {
        request.result.createObjectStore(AUDIO_STORE_NAME, { keyPath: "id" })
      }
    }
    request.onsuccess = () => resolve(request.result)
    request.onerror = () => reject(request.error)
  })
}

async function saveVoiceAttachment(id, blob) {
  const db = await openVoiceDb()
  await new Promise((resolve, reject) => {
    const transaction = db.transaction(AUDIO_STORE_NAME, "readwrite")
    const store = transaction.objectStore(AUDIO_STORE_NAME)
    const request = store.getAll()
    request.onsuccess = () => {
      const records = (request.result || []).filter(item => item.id !== id).sort((a, b) => a.createdAt - b.createdAt)
      records.slice(0, Math.max(0, records.length - MAX_STORED_AUDIO + 1)).forEach(item => store.delete(item.id))
      store.put({ id, blob, createdAt: Date.now() })
    }
    request.onerror = () => reject(request.error)
    transaction.oncomplete = resolve
    transaction.onerror = () => reject(transaction.error)
    transaction.onabort = () => reject(transaction.error)
  })
  db.close()
}

async function getVoiceAttachment(id) {
  const db = await openVoiceDb()
  const blob = await new Promise((resolve, reject) => {
    const request = db.transaction(AUDIO_STORE_NAME, "readonly").objectStore(AUDIO_STORE_NAME).get(id)
    request.onsuccess = () => resolve(request.result?.blob || null)
    request.onerror = () => reject(request.error)
  })
  db.close()
  return blob
}

async function pruneVoiceAttachments(retainedIds = null) {
  try {
    const db = await openVoiceDb()
    await new Promise((resolve, reject) => {
      const transaction = db.transaction(AUDIO_STORE_NAME, "readwrite")
      const store = transaction.objectStore(AUDIO_STORE_NAME)
      const request = store.getAll()
      request.onsuccess = () => {
        const records = request.result || []
        const retained = retainedIds === null
          ? records
          : records.filter(item => new Set(retainedIds).has(item.id))
        if (retainedIds !== null) {
          records.filter(item => !new Set(retainedIds).has(item.id)).forEach(item => store.delete(item.id))
        }
        retained.sort((a, b) => a.createdAt - b.createdAt)
          .slice(0, Math.max(0, retained.length - MAX_STORED_AUDIO))
          .forEach(item => store.delete(item.id))
      }
      request.onerror = () => reject(request.error)
      transaction.oncomplete = resolve
      transaction.onerror = () => reject(transaction.error)
      transaction.onabort = () => reject(transaction.error)
    })
    db.close()
  } catch {
    // Audio playback remains available for this page session via its object URL.
  }
}

async function hydrateVoiceAttachments(msgs) {
  for (const message of msgs) {
    if (!message.voice || !message.audioId || message.audioUrl) continue
    try {
      const blob = await getVoiceAttachment(message.audioId)
      if (blob) message.audioUrl = URL.createObjectURL(blob)
      else message.audioUnavailable = true
    } catch {
      message.audioUnavailable = true
    }
  }
}

export const useAssistantStore = defineStore("assistant", () => {
  const authStore = useAuthStore()
  const identityKey = () => assistantIdentityKey(authStore.user)
  const storageKey = () => STORAGE_PREFIX + ":" + identityKey()
  const sessionStorageKey = () => SESSION_PREFIX + ":" + identityKey()
  const loadScopedHistory = () => {
    try {
      const raw = localStorage.getItem(storageKey())
      return raw ? JSON.parse(raw) : []
    } catch { return [] }
  }

  // ── State ────────────────────────────────────────────────────────────
  const messages = ref(loadScopedHistory())
  const isLoading = ref(false)
  const error = ref(null)

  // Suggestions rapides affichées sur l'écran vide
  const quickSuggestions = [
    {
      id: 1,
      title: "État financier",
      text: "Quel est l'état financier actuel ?",
      icon: "pi pi-wallet",
    },
    {
      id: 2,
      title: "Projets actifs",
      text: "Combien de projets sont actifs ?",
      icon: "pi pi-briefcase",
    },
    {
      id: 3,
      title: "Campagne principale",
      text: "Quelle campagne couvre le plus de bénéficiaires ?",
      icon: "pi pi-users",
    },
    {
      id: 4,
      title: "Bénéficiaires par région",
      text: "Répartition des bénéficiaires par région",
      icon: "pi pi-map",
    },
    {
      id: 5,
      title: "Alertes prioritaires",
      text: "Quelles sont les alertes prioritaires ?",
      icon: "pi pi-exclamation-triangle",
    },
    {
      id: 6,
      title: "Résumé du mois",
      text: "Génère un résumé exécutif du mois",
      icon: "pi pi-chart-bar",
    },
  ]

  void hydrateVoiceAttachments(messages.value)

  // ── Persistance automatique ──────────────────────────────────────────
  // Sauvegarde chaque fois que messages change (hors placeholders)
  watch(
    messages,
    (msgs) => saveHistory(msgs, storageKey()),
    { deep: true }
  )
  watch(identityKey, () => {
    messages.value.forEach(message => { if (message.audioUrl) URL.revokeObjectURL(message.audioUrl) })
    clearAssistantHistoryStorage()
    messages.value = []
  })

  // ── Getters ──────────────────────────────────────────────────────────
  const hasMessages = computed(() => messages.value.length > 0)
  const lastMessage = computed(() => messages.value[messages.value.length - 1] ?? null)

  // Historique envoyé à l'API (sans les placeholders, max 10 derniers échanges)
  // ── Actions ──────────────────────────────────────────────────────────
  const clearHistory = () => {
    messages.value.forEach(message => { if (message.audioUrl) URL.revokeObjectURL(message.audioUrl) })
    messages.value = []
    error.value = null
    localStorage.removeItem(storageKey())
    localStorage.removeItem(sessionStorageKey())
    void pruneVoiceAttachments([])
  }

  const restoreVoiceAudio = () => hydrateVoiceAttachments(messages.value)

  const _pushMessage = (role, content, extra = {}) => {
    const msg = {
      id: `${role}-${Date.now()}-${Math.random().toString(36).slice(2, 7)}`,
      role,
      content,
      timestamp: new Date().toISOString(),
      ...extra,
    }
    messages.value.push(msg)
    return msg
  }

  const sendMessage = async (question, options = {}) => {
    if (!question?.trim() || isLoading.value) return false

    error.value = null

    // 1. Message utilisateur. Audio stays in local IndexedDB; only the transcript is sent to Django.
    let voiceMetadata = {}
    if (options.voiceBlob instanceof Blob) {
      const audioId = globalThis.crypto?.randomUUID?.() || `audio-${Date.now()}-${Math.random().toString(36).slice(2)}`
      const audioUrl = URL.createObjectURL(options.voiceBlob)
      voiceMetadata = {
        voice: true,
        audioId,
        audioUrl,
        durationSeconds: options.voiceDuration || 0,
        transcription: question.trim(),
      }
      try {
        await saveVoiceAttachment(audioId, options.voiceBlob)
      } catch {
        // Keep playback in the current session even if browser storage is unavailable.
      }
    }
    _pushMessage("user", question.trim(), voiceMetadata)

    // 2. Placeholder assistant (bulle de chargement)
    const placeholder = _pushMessage("assistant", "", {
      loading: true,
      voiceResponse: options.voiceBlob instanceof Blob,
    })

    isLoading.value = true

    try {
      const res = await api.post("/api/assistant/chat/", {
        question: question.trim(),
        session_id: localStorage.getItem(sessionStorageKey()) || undefined,
      })
      if (res.data?.session_id) localStorage.setItem(sessionStorageKey(), res.data.session_id)

      // 3. Remplacer le placeholder par la vraie réponse
      const idx = messages.value.findIndex(m => m.id === placeholder.id)
      if (idx !== -1) {
        messages.value[idx] = {
          ...messages.value[idx],
          content: res.data.answer ?? "Aucune réponse reçue.",
          timestamp: res.data.generated_at ?? new Date().toISOString(),
          loading: false,
        }
      }
      return true
    } catch (err) {
      const errMsg =
        err.response?.data?.detail ??
        err.response?.data?.answer ??
        "Le service IA est momentanément indisponible."

      const idx = messages.value.findIndex(m => m.id === placeholder.id)
      if (idx !== -1) {
        messages.value[idx] = {
          ...messages.value[idx],
          content: errMsg,
          loading: false,
          isError: true,
        }
      }
      error.value = errMsg
      return false
    } finally {
      isLoading.value = false
    }
  }

  return {
    messages,
    isLoading,
    error,
    quickSuggestions,
    hasMessages,
    lastMessage,
    clearHistory,
    restoreVoiceAudio,
    sendMessage,
  }
})
