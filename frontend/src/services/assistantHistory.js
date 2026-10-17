const HISTORY_PREFIXES = [
  "barakagive_assistant_history",
  "barakagive_finance_assistant_history",
  "barakagive_assistant_session",
]

const AUDIO_DATABASES = ["BarakaGiveAssistantAudio", "BarakaGiveFinanceVoice"]

export function assistantIdentityKey(user) {
  return user
    ? String(user.organization || "no-org") + ":" + String(user.id || user.email || "unknown")
    : "anonymous"
}

export function redactHistoryText(text) {
  return String(text ?? "")
    .replace(/\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b/gi, "[email masque]")
    .replace(/(?<!\w)(?:\+?221[ .-]?)?7(?:[ .-]?\d){8}(?!\w)(?!\s*(?:FCFA|XOF|EUR|USD))/gi, "[telephone masque]")
    .replace(/(?<!\w)0(?:[ .-]?\d){9}(?!\w)(?!\s*(?:FCFA|XOF|EUR|USD))/gi, "[telephone masque]")
    .replace(/\b(?:adresse|address)\s*[:=]\s*[^,;\n]{5,100}/gi, "adresse [masquee]")
}

export function clearLegacyAssistantHistory() {
  try { localStorage.removeItem("barakagive_assistant_history") } catch { /* best effort */ }
}

export function clearAssistantHistoryStorage() {
  try {
    const keys = []
    for (let index = 0; index < localStorage.length; index += 1) {
      const key = localStorage.key(index)
      if (key) keys.push(key)
    }
    for (const key of keys) {
      if (HISTORY_PREFIXES.some(prefix => key === prefix || key.startsWith(prefix + ":"))) {
        localStorage.removeItem(key)
      }
    }
  } catch {
    // Storage may be unavailable in private browsing.
  }

  if (globalThis.indexedDB) {
    for (const name of AUDIO_DATABASES) {
      try { globalThis.indexedDB.deleteDatabase(name) } catch { /* best effort */ }
    }
  }
}
