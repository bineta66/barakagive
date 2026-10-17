<template>
  <div class="flex h-screen bg-white overflow-hidden">

    <!-- ── Sidebar historique ─────────────────────────────────────── -->
    <aside class="w-72 border-r border-slate-200/60 flex flex-col bg-gradient-to-b from-white to-slate-50/30 flex-shrink-0">
      <!-- Header sidebar -->
      <div class="p-4 border-b border-slate-200/60">
        <div class="flex items-center justify-between">
          <div class="flex items-center gap-2.5">
            <div class="w-8 h-8 rounded-lg bg-[#021427] border border-[#CCA43B]/40
                        flex items-center justify-center flex-shrink-0">
              <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16"
                   viewBox="0 0 24 24" fill="none" stroke="#CCA43B"
                   stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
                <circle cx="12" cy="12" r="8"/>
                <path d="M9.5 9.5c.5-1 1.5-1.5 2.5-1.5 1.4 0 2.5.9 2.5 2s-.8 1.5-2 2c-1.2.5-2 1-2 2.5"/>
                <path d="M12 18v-1.5"/>
              </svg>
            </div>
            <span class="font-semibold text-[#021427] text-sm">Assistant Finance</span>
          </div>
          <button
            @click="startNew"
            class="p-1.5 hover:bg-slate-100 rounded-lg transition-colors"
            title="Nouvelle conversation"
          >
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24"
                 fill="none" stroke="#021427" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M5 12h14"/><path d="M12 5v14"/>
            </svg>
          </button>
        </div>

        <!-- Indicateur alerte -->
        <div class="mt-3 flex items-center gap-2 px-3 py-2 rounded-lg"
             :class="alertBannerClass">
          <span class="w-2 h-2 rounded-full flex-shrink-0" :class="alertDotClass"/>
          <span class="text-xs font-semibold" :class="alertTextClass">
            {{ alertLabel }}
          </span>
        </div>
      </div>

      <!-- Liste conversations -->
      <div class="flex-1 overflow-y-auto p-3 space-y-1">
        <div v-if="conversations.length === 0"
             class="text-center py-8 text-slate-400 text-xs">
          Aucune conversation pour le moment
        </div>
        <button
          v-for="conv in conversations"
          :key="conv.id"
          @click="loadConv(conv.id)"
          :class="[
            'w-full text-left p-3 rounded-lg transition-all duration-200 border',
            currentId === conv.id
              ? 'bg-[#021427]/5 border-[#CCA43B]/30'
              : 'hover:bg-slate-100 border-transparent',
          ]"
        >
          <div class="flex items-start justify-between gap-2">
            <div class="flex-1 min-w-0">
              <p class="text-xs font-semibold text-[#021427] truncate">{{ conv.title }}</p>
              <p class="text-[10px] text-slate-400 mt-0.5">{{ relativeTime(conv.lastUpdate) }}</p>
            </div>
            <button
              @click.stop="deleteConv(conv.id)"
              class="p-1 hover:bg-red-100 rounded text-slate-400 hover:text-red-600 transition-colors flex-shrink-0"
            >
              <svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24"
                   fill="none" stroke="currentColor" stroke-width="2"
                   stroke-linecap="round" stroke-linejoin="round">
                <path d="M3 6h18"/><path d="M19 6v14c0 1-1 2-2 2H7c-1 0-2-1-2-2V6"/>
                <path d="M8 6V4c0-1 1-2 2-2h4c1 0 2 1 2 2v2"/>
              </svg>
            </button>
          </div>
        </button>
      </div>

      <!-- Utilisateur -->
      <div class="p-4 border-t border-slate-200/60 bg-white">
        <div class="flex items-center gap-3">
          <div class="w-9 h-9 rounded-full bg-[#021427] border border-[#CCA43B]/40
                      flex items-center justify-center text-[#CCA43B] font-bold text-sm flex-shrink-0">
            {{ userInitials }}
          </div>
          <div class="flex-1 min-w-0">
            <p class="text-xs font-semibold text-[#021427] truncate">{{ userName }}</p>
            <p class="text-[10px] text-slate-500">Responsable Finance</p>
          </div>
        </div>
      </div>
    </aside>

    <!-- ── Zone chat principale ───────────────────────────────────── -->
    <main class="flex-1 flex flex-col overflow-hidden">
      <!-- Header -->
      <header class="h-16 border-b border-slate-200/60 px-6 flex items-center justify-between bg-white flex-shrink-0">
        <div class="flex items-center gap-3">
          <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24"
               fill="none" stroke="#021427" stroke-width="1.8"
               stroke-linecap="round" stroke-linejoin="round">
            <circle cx="12" cy="12" r="8"/>
            <path d="M9.5 9.5c.5-1 1.5-1.5 2.5-1.5 1.4 0 2.5.9 2.5 2s-.8 1.5-2 2c-1.2.5-2 1-2 2.5"/>
            <path d="M12 18v-1.5"/>
          </svg>
          <div>
            <h1 class="text-base font-bold text-[#021427]">Contrôleur Financier IA</h1>
            <p class="text-[11px] text-slate-500">Analyse en temps réel de vos données financières</p>
          </div>
        </div>
        <div class="flex items-center gap-2">
          <button
            v-if="store.hasMessages"
            @click="store.clearHistory(); startNew()"
            class="text-xs text-slate-500 hover:text-red-600 font-medium transition-colors px-3 py-1.5 rounded-lg hover:bg-red-50"
          >
            Effacer
          </button>
          <span class="flex items-center gap-1.5 text-xs" :class="store.alertColors.text">
            <span class="w-2 h-2 rounded-full" :class="alertDotClass"/>
            {{ alertLabel }}
          </span>
        </div>
      </header>

      <!-- Messages -->
      <div
        ref="messagesContainer"
        class="flex-1 overflow-y-auto px-6 py-6"
        :class="{ 'flex items-center justify-center': !store.hasMessages }"
      >
        <!-- Écran d'accueil -->
        <div v-if="!store.hasMessages" class="max-w-2xl w-full">
          <div class="text-center mb-8">
            <div class="w-20 h-20 mx-auto mb-4 rounded-2xl bg-[#021427] border border-[#CCA43B]/30
                        flex items-center justify-center shadow-xl">
              <svg xmlns="http://www.w3.org/2000/svg" width="34" height="34"
                   viewBox="0 0 24 24" fill="none" stroke="#CCA43B"
                   stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
                <circle cx="12" cy="12" r="8"/>
                <path d="M9.5 9.5c.5-1 1.5-1.5 2.5-1.5 1.4 0 2.5.9 2.5 2s-.8 1.5-2 2c-1.2.5-2 1-2 2.5"/>
                <path d="M12 18v-1.5"/>
              </svg>
            </div>
            <h2 class="text-xl font-bold text-[#021427] mb-2">Bonjour {{ firstName }} 👋</h2>
            <p class="text-sm text-slate-600">Comment puis-je vous aider aujourd'hui ?</p>
          </div>

          <!-- Cards insight initiales -->
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-3 mb-6">
            <FinanceInsightCard
              type="info"
              label="Synthèse budgétaire"
              content="Consultez le taux d'exécution, le solde disponible et les budgets actifs."
            />
            <FinanceInsightCard
              type="warning"
              label="Conformité"
              content="Vérifiez les justificatifs en attente et les dépenses sans pièce justificative."
            />
            <FinanceInsightCard
              type="success"
              label="Dons & financements"
              content="Suivez les derniers dons reçus et l'état des bailleurs actifs."
            />
            <FinanceInsightCard
              type="info"
              label="Projection"
              content="Estimez la durée de vie du budget au rythme de dépenses actuel."
            />
          </div>

          <!-- Suggestions rapides -->
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-2">
            <button
              v-for="s in store.quickSuggestions"
              :key="s.id"
              @click="handleQuickSuggestion(s.text)"
              class="p-4 text-left rounded-xl border border-slate-200/60
                     hover:border-[#CCA43B]/50 hover:bg-[#CCA43B]/5
                     transition-all duration-200 group"
            >
              <div class="flex items-start gap-3">
                <div class="w-9 h-9 rounded-lg bg-[#021427]/8 border border-[#021427]/10
                            flex items-center justify-center flex-shrink-0
                            group-hover:bg-[#021427]/15 transition-colors">
                  <i :class="['text-[#021427] text-sm', s.icon]"/>
                </div>
                <div>
                  <p class="text-xs font-semibold text-[#021427] mb-0.5">{{ s.title }}</p>
                  <p class="text-[11px] text-slate-500 line-clamp-2">{{ s.text }}</p>
                </div>
              </div>
            </button>
          </div>
        </div>

        <!-- Liste des messages -->
        <div v-else class="max-w-3xl mx-auto w-full space-y-5">
          <FinanceChatMessage
            v-for="msg in store.messages"
            :key="msg.id"
            :message="msg"
          />
          <div v-if="store.isLoading" class="flex justify-start">
            <div class="max-w-[80%] bg-slate-100 rounded-2xl p-4">
              <div class="flex items-center gap-2 text-slate-500">
                <svg class="w-4 h-4 animate-spin" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/>
                </svg>
                <span class="text-sm">Analyse financière en cours…</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Input fixe -->
      <div class="border-t border-slate-200/60 bg-white p-4 flex-shrink-0">
        <div class="max-w-3xl mx-auto">
          <FinanceChatInput
            :disabled="store.isLoading"
            @send="handleSend"
          />
        </div>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, nextTick, watch } from "vue"
import { storeToRefs } from "pinia"
import { useFinanceAssistantStore } from "@/stores/financeAssistant.js"
import { useAuthStore } from "@/stores/auth.js"
import FinanceChatMessage from "@/modules/finance/components/ia/FinanceChatMessage.vue"
import FinanceChatInput   from "@/modules/finance/components/ia/FinanceChatInput.vue"
import FinanceInsightCard from "@/modules/finance/components/ia/FinanceInsightCard.vue"

const store     = useFinanceAssistantStore()
const authStore = useAuthStore()

const { messages, isLoading, alertLevel, alertColors, quickSuggestions } = storeToRefs(store)

const messagesContainer = ref(null)

// ── Infos utilisateur ────────────────────────────────────────────
const userName    = computed(() => authStore.user?.nom_complet || "Utilisateur")
const firstName   = computed(() => userName.value.split(" ")[0])
const userInitials = computed(() =>
  userName.value.split(" ").map(n => n[0]).join("").toUpperCase().slice(0, 2)
)

// ── Alerte ───────────────────────────────────────────────────────
const alertDotClass = computed(() => ({
  RED:    "bg-rose-baraka animate-pulse",
  ORANGE: "bg-rose-baraka/80",
  YELLOW: "bg-bleu-accent",
  GREEN:  "bg-bleu-accent",
}[alertLevel.value] || "bg-bleu-accent"))

const alertTextClass = computed(() => ({
  RED:    "text-rose-baraka font-semibold",
  ORANGE: "text-rose-baraka",
  YELLOW: "text-bleu-accent",
  GREEN:  "text-bleu-accent",
}[alertLevel.value] || "text-bleu-accent"))

const alertLabel = computed(() => ({
  RED:    "Alerte Critique",
  ORANGE: "Alerte Risque",
  YELLOW: "Alerte Vigilance",
  GREEN:  "Situation normale",
}[alertLevel.value] || "Situation normale"))

const alertBannerClass = computed(() => ({
  RED:    "bg-red-50 border border-red-200",
  ORANGE: "bg-orange-50 border border-orange-200",
  YELLOW: "bg-amber-50 border border-amber-200",
  GREEN:  "bg-emerald-50 border border-emerald-200",
}[alertLevel.value] || "bg-emerald-50 border border-emerald-200"))

// ── Gestion des messages ─────────────────────────────────────────
watch(messages, async () => {
  await nextTick()
  if (messagesContainer.value) {
    messagesContainer.value.scrollTo({ top: messagesContainer.value.scrollHeight, behavior: "smooth" })
  }
}, { deep: true })

const handleSend = async (text, clearDraft) => {
  const q = (typeof text === "string" ? text : "").trim()
  if (!q || isLoading.value) return
  const sent = await store.sendMessage(q)
  if (sent) clearDraft?.()
  updateConv()
}

const handleQuickSuggestion = async (text) => {
  if (!text || isLoading.value) return
  await store.sendMessage(text.trim())
  updateConv()
}

// ── Gestion de l'historique des conversations ────────────────────
const conversations = ref([])
const currentId     = ref(null)
const CONV_KEY      = "barakagive_finance_conversations"

const loadConversations = () => {
  try {
    const raw = localStorage.getItem(CONV_KEY)
    if (raw) conversations.value = JSON.parse(raw)
  } catch { /* silencieux */ }
}

const saveConversations = () => {
  try {
    localStorage.setItem(CONV_KEY, JSON.stringify(conversations.value))
  } catch { /* silencieux */ }
}

const startNew = () => {
  if (messages.value.length > 0 && currentId.value) updateConv()
  currentId.value = Date.now().toString()
  store.messages = []
  store.error    = null
}

const updateConv = () => {
  if (!currentId.value || messages.value.length === 0) return
  const title  = messages.value[0]?.content?.slice(0, 55) || "Nouvelle conversation"
  const conv   = { id: currentId.value, title, messages: [...messages.value], lastUpdate: Date.now() }
  const idx    = conversations.value.findIndex(c => c.id === currentId.value)
  if (idx >= 0) conversations.value[idx] = conv
  else conversations.value.unshift(conv)
  if (conversations.value.length > 50) conversations.value = conversations.value.slice(0, 50)
  saveConversations()
}

const loadConv = (id) => {
  const found = conversations.value.find(c => c.id === id)
  if (!found) return
  currentId.value   = id
  store.messages    = [...found.messages]
}

const deleteConv = (id) => {
  conversations.value = conversations.value.filter(c => c.id !== id)
  saveConversations()
  if (currentId.value === id) startNew()
}

const relativeTime = (ts) => {
  const diff = Date.now() - ts
  const m = Math.floor(diff / 60000)
  const h = Math.floor(diff / 3600000)
  const d = Math.floor(diff / 86400000)
  if (m < 1) return "À l'instant"
  if (m < 60) return `Il y a ${m}min`
  if (h < 24) return `Il y a ${h}h`
  if (d < 7)  return `Il y a ${d}j`
  return new Date(ts).toLocaleDateString("fr-FR", { day: "numeric", month: "short" })
}

onMounted(() => {
  store.fetchAlertStatus()
  loadConversations()
  if (!currentId.value) currentId.value = Date.now().toString()
  // Sauvegarde auto toutes les 30s
  setInterval(() => { if (messages.value.length > 0) updateConv() }, 30_000)
})
</script>

<style scoped>
.overflow-y-auto::-webkit-scrollbar { width: 5px; }
.overflow-y-auto::-webkit-scrollbar-track { background: transparent; }
.overflow-y-auto::-webkit-scrollbar-thumb { background: #cbd5e1; border-radius: 3px; }
</style>
