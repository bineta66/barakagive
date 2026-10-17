<template>
  <div v-if="isGerant">
    <!-- Floating Orb (Visible uniquement pour le Gérant) -->
    <div
      class="fixed bottom-24 lg:bottom-6 right-4 sm:right-6 z-40 cursor-pointer transition-transform duration-300 hover:scale-110 select-none group"
      @click="toggleDrawer"
      title="Ouvrir l'Assistant IA du Gérant"
    >
      <div
        class="relative flex items-center justify-center w-16 h-16 rounded-full bg-[#021B30]/95 backdrop-blur-md shadow-2xl border-2 border-[#CCA43B]/60 transition-all duration-300 group-hover:border-[#CCA43B] group-hover:shadow-[#CCA43B]/20"
        :class="orbAnimationClasses"
      >
        <span class="text-[#CCA43B] transition-transform duration-300 group-hover:rotate-12">
          <svg xmlns="http://www.w3.org/2000/svg" width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M12 2v4M12 18v4M4.93 4.93l2.83 2.83M16.24 16.24l2.83 2.83M2 12h4M18 12h4M4.93 19.07l2.83-2.83M16.24 7.76l2.83-2.83"/>
          </svg>
        </span>

        <!-- Ping Rings for Attention -->
        <span
          v-if="hasAlerts"
          class="absolute inset-0 rounded-full border-2 border-rose-baraka animate-ping opacity-60 pointer-events-none"
        ></span>
        <span
          v-else
          class="absolute inset-0 rounded-full border border-[#CCA43B] animate-pulse opacity-40 pointer-events-none"
        ></span>

        <!-- Alert Counter Badge -->
        <span
          v-if="hasAlerts"
          class="absolute -top-1 -right-1 flex h-5 w-5 items-center justify-center rounded-full bg-rose-baraka text-[10px] font-bold text-white shadow-md border-2 border-[#021B30]"
        >
          !
        </span>
      </div>
    </div>

    <!-- Slide-over Drawer -->
    <transition name="slide-drawer">
      <div
        v-if="isOpen"
        class="fixed inset-y-0 right-0 z-[70] w-full max-w-md bg-white/95 backdrop-blur-2xl shadow-2xl border-l border-slate-200 flex flex-col overflow-hidden text-slate-800"
      >
        <!-- Header -->
        <div class="px-6 py-5 border-b border-slate-100 bg-[#021B30] text-white flex items-center justify-between shadow-sm">
          <div class="flex items-center gap-3">
            <div class="w-10 h-10 rounded-xl bg-[#CCA43B]/20 border border-[#CCA43B]/40 flex items-center justify-center text-[#CCA43B]">
              <svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M9.937 15.5A2 2 0 0 0 8.5 14.063l-6.135-1.582a.5.5 0 0 1 0-.962L8.5 9.936A2 2 0 0 0 9.937 8.5l1.582-6.135a.5.5 0 0 1 .963 0L14.063 8.5A2 2 0 0 0 15.5 9.937l6.135 1.581a.5.5 0 0 1 0 .964L15.5 14.063a2 2 0 0 0-1.437 1.437l-1.582 6.135a.5.5 0 0 1-.963 0z"/><path d="M20 3v4"/><path d="M22 5h-4"/><path d="M4 17v2"/><path d="M5 18H3"/>
              </svg>
            </div>
            <div>
              <h2 class="text-base font-bold text-white flex items-center gap-2">
                Assistant IA du Gérant
              </h2>
              <p class="text-xs text-slate-300">Données réelles synchronisées</p>
            </div>
          </div>

          <div class="flex items-center gap-1">
            <button
              @click="activeTab = 'chat'"
              class="rounded-lg px-2.5 py-1.5 text-xs font-semibold transition"
              :class="activeTab === 'chat' ? 'bg-white text-[#021B30]' : 'text-white/75 hover:bg-white/10'"
            >Conversation</button>
            <button
              @click="activeTab = 'dashboard'"
              class="rounded-lg px-2.5 py-1.5 text-xs font-semibold transition"
              :class="activeTab === 'dashboard' ? 'bg-white text-[#021B30]' : 'text-white/75 hover:bg-white/10'"
            >Vue d’ensemble</button>
            <button
              @click="fetchAssistantData"
              :disabled="loading"
              class="p-2 text-slate-300 hover:text-[#CCA43B] hover:bg-white/10 rounded-lg transition disabled:opacity-50"
              title="Actualiser les données"
            >
              <svg
                xmlns="http://www.w3.org/2000/svg"
                width="18"
                height="18"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="2"
                stroke-linecap="round"
                stroke-linejoin="round"
                :class="{ 'animate-spin': loading }"
              >
                <path d="M3 12a9 9 0 0 1 9-9 9.75 9.75 0 0 1 6.74 2.74L21 8"/><path d="M21 3v5h-5"/><path d="M21 12a9 9 0 0 1-9 9 9.75 9.75 0 0 1-6.74-2.74L3 16"/><path d="M8 16H3v5"/>
              </svg>
            </button>
            <button
              @click="isOpen = false"
              class="p-2 text-slate-300 hover:text-white hover:bg-white/10 rounded-lg transition"
              title="Fermer"
            >
              <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M18 6 6 18"/><path d="m6 6 12 12"/>
              </svg>
            </button>
          </div>
        </div>

        <!-- Content Area -->
        <div class="flex-1 min-h-0 overflow-y-auto">
          <section v-if="activeTab === 'chat'" class="flex h-full min-h-[30rem] flex-col bg-slate-50/70">
            <div ref="chatScroll" class="flex-1 space-y-4 overflow-y-auto p-4 sm:p-6">
              <div v-if="messages.length === 0" class="mx-auto max-w-sm py-10 text-center">
                <div class="mx-auto mb-4 flex h-12 w-12 items-center justify-center rounded-2xl bg-[#021B30] text-[#CCA43B]">✦</div>
                <h3 class="text-base font-bold text-[#021B30]">Comment puis-je vous aider ?</h3>
                <p class="mt-2 text-sm text-slate-500">Je peux rechercher dans les données de votre ONG et préparer une synthèse. Les chiffres affichés viennent de Django.</p>
                <div class="mt-5 flex flex-wrap justify-center gap-2">
                  <button v-for="suggestion in suggestions" :key="suggestion" @click="sendChat(suggestion)" class="rounded-full border border-slate-200 bg-white px-3 py-2 text-xs font-medium text-slate-700 hover:border-[#CCA43B]">{{ suggestion }}</button>
                </div>
              </div>

              <article v-for="(message, index) in messages" :key="`${sessionId}-${index}`" class="flex" :class="message.role === 'user' ? 'justify-end' : 'justify-start'">
                <div class="max-w-[92%] space-y-3" :class="message.role === 'user' ? 'items-end' : 'items-start'">
                  <div class="whitespace-pre-wrap rounded-2xl px-4 py-3 text-sm leading-relaxed" :class="message.role === 'user' ? 'rounded-br-md bg-[#021B30] text-white' : 'rounded-bl-md border border-slate-200 bg-white text-slate-800'">{{ message.content }}</div>
                  <div v-if="message.tool_results?.length" class="space-y-2">
                    <div v-for="result in message.tool_results" :key="result.tool" class="rounded-xl border border-slate-200 bg-white p-3">
                      <h4 class="text-xs font-bold text-[#021B30]">{{ result.title }}</h4>
                      <div v-if="result.action" class="mt-2 space-y-2">
                        <p class="text-xs leading-relaxed text-slate-600">{{ result.action.message }}</p>
                        <ul v-if="result.action.required_fields?.length" class="list-inside list-disc space-y-1 text-xs text-slate-500">
                          <li v-for="field in result.action.required_fields" :key="field">{{ field }}</li>
                        </ul>
                        <button v-if="result.action.route" type="button" @click="openActionRoute(result.action.route)" class="inline-flex rounded-lg bg-[#021B30] px-3 py-2 text-xs font-semibold text-white hover:bg-[#00313C]">
                          Ouvrir le formulaire
                        </button>
                      </div>
                      <p v-if="result.data?.message" class="mt-1 text-xs text-slate-600">{{ result.data.message }}</p>
                      <p v-else-if="result.data?.total !== undefined" class="mt-1 text-sm font-semibold text-slate-800">{{ result.data.total }} résultat(s)</p>
                      <div v-if="result.data?.sent !== undefined" class="mt-2 space-y-1 text-xs text-slate-600">
                        <p v-if="result.data.sent > 0" class="font-semibold text-[#00313C]">{{ result.data.sent }} notification(s) interne(s) envoyée(s).</p>
                        <p v-for="(notification, notificationIndex) in result.data.notifications" :key="notification.notification_id || notificationIndex">
                          {{ notification.project }} · {{ notification.recipient }}
                        </p>
                        <p v-for="candidate in result.data.candidates || []" :key="candidate.id" class="rounded-lg bg-slate-50 px-2 py-1">
                          {{ candidate.name }}
                        </p>
                      </div>
                      <ul v-if="result.data?.par_region?.length" class="mt-2 space-y-1 text-xs text-slate-600">
                        <li v-for="region in result.data.par_region" :key="region['zone__region__nom']">
                          {{ region['zone__region__nom'] || 'Région non précisée' }} · {{ region.total }} prioritaire(s)
                        </li>
                      </ul>
                      <p v-if="result.data?.beneficiaires_avec_action !== undefined" class="mt-2 text-xs text-slate-600">
                        {{ result.data.beneficiaires_avec_action }} bénéficiaire(s) avec aide réalisée · {{ result.data.actions_realisees }} action(s)
                      </p>
                      <ul v-if="Array.isArray(result.data) && result.data.length" class="mt-2 space-y-1.5">
                        <li v-for="(item, itemIndex) in result.data.slice(0, 8)" :key="item.id || itemIndex" class="text-xs text-slate-600">
                          <span class="font-semibold text-slate-800">{{ item.name || item.nom || item.projet__name || item.type || 'Activité' }}</span>
                          <span v-if="item.region || item.region__nom"> · {{ item.region || item.region__nom }}</span>
                          <span v-if="item.montant !== undefined"> · {{ formatMoney(item.montant) }}</span>
                          <span v-if="item.statut"> · {{ item.statut }}</span>
                          <span v-if="item.end_date"> · échéance {{ formatDate(item.end_date) }}</span>
                          <span v-if="item.chef_projet__first_name || item.chef_projet__last_name"> · {{ [item.chef_projet__first_name, item.chef_projet__last_name].filter(Boolean).join(' ') }}</span>
                          <span v-if="item.date"> · {{ formatDate(item.date) }}</span>
                        </li>
                        <li v-if="result.data.length > 8" class="text-xs text-slate-400">+ {{ result.data.length - 8 }} autres éléments</li>
                      </ul>
                      <div v-if="result.data?.budget_total !== undefined" class="mt-2 grid grid-cols-2 gap-2 text-xs text-slate-600">
                        <span>Budget : <b>{{ formatMoney(result.data.budget_total) }}</b></span>
                        <span>Dépenses : <b>{{ formatMoney(result.data.depenses) }}</b></span>
                        <span>Dons : <b>{{ formatMoney(result.data.dons) }}</b></span>
                        <span>Solde : <b>{{ formatMoney(result.data.solde_dons_moins_depenses) }}</b></span>
                      </div>
                    </div>
                  </div>
                  <button v-if="message.role === 'assistant' && message.content" type="button" @click="speak(message.content)" class="text-[11px] font-medium text-slate-400 hover:text-[#021B30]">Écouter la réponse</button>
                </div>
              </article>

              <div v-if="chatLoading" class="flex items-center gap-2 text-sm text-slate-500">
                <span class="h-2 w-2 animate-pulse rounded-full bg-[#CCA43B]"></span> L’assistant analyse les données…
              </div>
            </div>

            <form @submit.prevent="sendChat()" class="border-t border-slate-200 bg-white p-3 sm:p-4">
              <div class="flex items-end gap-2 rounded-2xl border border-slate-300 bg-white p-2 focus-within:border-[#021B30] focus-within:ring-2 focus-within:ring-[#021B30]/10">
                <textarea v-model="chatInput" rows="1" maxlength="4000" placeholder="Posez une question sur votre ONG…" class="max-h-32 min-h-10 flex-1 resize-y border-0 bg-transparent px-2 py-2 text-sm text-slate-800 outline-none placeholder:text-slate-400 focus:ring-0" @keydown.enter.exact.prevent="sendChat()"></textarea>
                <button type="button" @click="toggleVoice" :disabled="!voiceSupported" class="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl text-[#021B30] hover:bg-slate-100 disabled:text-slate-300" :title="voiceListening ? 'Arrêter la dictée' : 'Dicter une demande'" :aria-pressed="voiceListening">
                  <svg v-if="!voiceListening" viewBox="0 0 24 24" class="h-5 w-5" fill="none" stroke="currentColor" stroke-width="1.8"><rect x="9" y="2" width="6" height="13" rx="3"/><path d="M5 10v2a7 7 0 0 0 14 0v-2M12 19v3m-4 0h8"/></svg>
                  <span v-else class="h-3 w-3 rounded-sm bg-rose-600"></span>
                </button>
                <button type="submit" :disabled="chatLoading || !chatInput.trim()" class="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-[#021B30] text-white hover:bg-[#00313C] disabled:opacity-40" aria-label="Envoyer">
                  <svg viewBox="0 0 24 24" class="h-5 w-5" fill="none" stroke="currentColor" stroke-width="2"><path d="m5 12 14-7-4 14-3-6-7-1Z"/><path d="m12 13 4-4"/></svg>
                </button>
              </div>
              <p class="mt-2 text-center text-[10px] text-slate-400">L’assistant prépare les actions sensibles ; Django valide les droits et les données avant toute exécution.</p>
              <p v-if="voiceError" class="mt-1 text-center text-xs text-rose-600">{{ voiceError }}</p>
            </form>
          </section>

          <div v-else class="p-6 space-y-6">
          <!-- Loader -->
          <div v-if="loading" class="flex flex-col items-center justify-center py-16 space-y-4">
            <div class="w-12 h-12 border-3 border-[#CCA43B] border-t-transparent rounded-full animate-spin"></div>
            <p class="text-sm font-medium text-slate-500">Calcul des données en temps réel depuis Django...</p>
          </div>

          <!-- Error State -->
          <div v-else-if="error" class="p-4 rounded-xl bg-red-50 border border-red-200 text-red-700 space-y-3">
            <p class="text-sm font-medium">{{ error }}</p>
            <button
              @click="fetchAssistantData"
              class="px-3 py-1.5 bg-red-600 text-white rounded-lg text-xs font-semibold hover:bg-red-700 transition"
            >
              Réessayer
            </button>
          </div>

          <!-- Live Real Data -->
          <template v-else-if="assistantData">
            <!-- Résumé Stratégique -->
            <div class="bg-gradient-to-br from-slate-50 to-amber-50/40 p-4 rounded-xl border border-slate-200/80 shadow-xs">
              <div class="flex items-center gap-2 mb-2 text-xs font-bold uppercase tracking-wider text-[#021B30]">
                <span class="w-2 h-2 rounded-full bg-[#CCA43B]"></span>
                Synthèse Opérationnelle
              </div>
              <p class="text-sm text-slate-700 leading-relaxed font-normal">
                {{ assistantData.resume }}
              </p>
            </div>

            <!-- Indicateurs Clés Métier (3 KPIs) -->
            <div class="grid grid-cols-1 gap-3 min-[360px]:grid-cols-2 sm:grid-cols-3">
              <div class="bg-white p-3.5 rounded-xl border border-slate-200 shadow-xs text-center">
                <span class="text-[11px] font-semibold text-slate-500 block uppercase">Projets</span>
                <span class="text-2xl font-bold text-[#021B30] mt-0.5 block">
                  {{ assistantData.projets_actifs }}
                </span>
                <span class="text-[10px] text-slate-400">Actifs</span>
              </div>

              <div class="bg-white p-3.5 rounded-xl border border-slate-200 shadow-xs text-center">
                <span class="text-[11px] font-semibold text-slate-500 block uppercase">Campagnes</span>
                <span class="text-2xl font-bold text-[#021B30] mt-0.5 block">
                  {{ assistantData.campagnes_actives }}
                </span>
                <span class="text-[10px] text-slate-400">En cours</span>
              </div>

              <div class="bg-white p-3.5 rounded-xl border border-slate-200 shadow-xs text-center">
                <span class="text-[11px] font-semibold text-slate-500 block uppercase">Bénéficiaires</span>
                <span class="text-2xl font-bold text-[#CCA43B] mt-0.5 block">
                  {{ assistantData.beneficiaires }}
                </span>
                <span class="text-[10px] text-slate-400">Enregistrés</span>
              </div>
            </div>

            <!-- Bilan Financier Réel -->
            <div class="bg-white rounded-xl border border-slate-200 p-4 shadow-xs space-y-3">
              <div class="flex items-center justify-between pb-2 border-b border-slate-100">
                <h3 class="text-xs font-bold uppercase tracking-wider text-slate-600">Bilan Financier Global</h3>
                <span
                  class="px-2 py-0.5 rounded text-[10px] font-bold"
                  :class="assistantData.solde < 0 ? 'bg-red-100 text-red-700' : 'bg-emerald-100 text-emerald-700'"
                >
                  {{ assistantData.solde < 0 ? 'Déficit' : 'Équilibré' }}
                </span>
              </div>

              <div class="grid grid-cols-2 gap-3 text-sm">
                <div>
                  <span class="text-xs text-slate-400 block">Budget Total</span>
                  <span class="font-bold text-[#021B30]">{{ formatMoney(assistantData.budget_total) }}</span>
                </div>
                <div>
                  <span class="text-xs text-slate-400 block">Dépenses</span>
                  <span class="font-bold text-slate-800">{{ formatMoney(assistantData.depenses) }}</span>
                </div>
              </div>

              <div class="pt-2 border-t border-slate-100 flex items-center justify-between">
                <div>
                  <span class="text-xs text-slate-400 block">Solde Restant</span>
                  <span class="text-base font-extrabold text-[#CCA43B]">
                    {{ formatMoney(assistantData.solde) }}
                  </span>
                </div>
                <div class="text-right">
                  <span class="text-xs text-slate-400 block">Exécution</span>
                  <span class="text-xs font-bold text-slate-700">{{ assistantData.taux_execution ?? 0 }} %</span>
                </div>
              </div>

              <!-- Execution progress bar -->
              <div class="w-full bg-slate-100 h-2 rounded-full overflow-hidden mt-1">
                <div
                  class="h-full rounded-full transition-all duration-500"
                  :class="(assistantData.taux_execution ?? 0) >= 80 ? 'bg-amber-500' : 'bg-[#021B30]'"
                  :style="{ width: `${Math.min(assistantData.taux_execution ?? 0, 100)}%` }"
                ></div>
              </div>
            </div>

            <!-- Alertes -->
            <div v-if="assistantData.alertes && assistantData.alertes.length" class="space-y-2">
              <h3 class="text-xs font-bold uppercase tracking-wider text-slate-600 flex items-center gap-1.5">
                <span class="w-1.5 h-1.5 rounded-full bg-red-500"></span>
                Alertes de Gestion ({{ assistantData.alertes.length }})
              </h3>
              <div class="space-y-2">
                <div
                  v-for="(alerte, idx) in assistantData.alertes"
                  :key="idx"
                  class="flex items-start gap-2.5 p-3 rounded-lg bg-amber-50/60 border border-amber-200/80 text-xs text-slate-800"
                >
                  <span class="text-amber-600 font-bold mt-0.5">⚠️</span>
                  <span>{{ alerte }}</span>
                </div>
              </div>
            </div>

            <!-- Recommandations -->
            <div v-if="assistantData.recommandations && assistantData.recommandations.length" class="space-y-2">
              <h3 class="text-xs font-bold uppercase tracking-wider text-slate-600 flex items-center gap-1.5">
                <span class="w-1.5 h-1.5 rounded-full bg-bleu-accent"></span>
                Recommandations Prioritaires
              </h3>
              <div class="space-y-2">
                <div
                  v-for="(rec, idx) in assistantData.recommandations"
                  :key="idx"
                  class="flex items-start gap-2.5 p-3 rounded-lg bg-slate-50 border border-slate-200/80 text-xs text-slate-700"
                >
                  <span class="w-4 h-4 rounded-full bg-[#021B30] text-white flex items-center justify-center text-[10px] font-bold shrink-0 mt-0.5">
                    {{ idx + 1 }}
                  </span>
                  <span>{{ rec }}</span>
                </div>
              </div>
            </div>

            <!-- Footer: Date de dernière mise à jour -->
            <div class="pt-4 border-t border-slate-100 text-center">
              <p class="text-[11px] text-slate-400">
                Dernière mise à jour : {{ formatTime(assistantData.generated_at) }}
              </p>
            </div>
          </template>
          </div>
        </div>
      </div>
    </transition>

    <!-- Backdrop Overlay -->
    <transition name="fade">
      <div
        v-if="isOpen"
        @click="isOpen = false"
        class="fixed inset-0 bg-black/30 z-[65] backdrop-blur-xs"
      ></div>
    </transition>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import api from '@/services/api'

const router = useRouter()
const authStore = useAuthStore()
const isGerant = computed(() => authStore.role === 'GERANT')

const isOpen = ref(false)
const loading = ref(false)
const error = ref(null)
const assistantData = ref(null)
const activeTab = ref('chat')
const chatInput = ref('')
const chatLoading = ref(false)
const messages = ref([])
const chatScroll = ref(null)
const voiceListening = ref(false)
const voiceError = ref('')
const sessionStorageKey = `barakagive_assistant_project_session_${authStore.user?.id || 'user'}_${authStore.organizationId || 'org'}`
const createSessionId = () => globalThis.crypto?.randomUUID?.() || 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, character => {
  const random = Math.random() * 16 | 0
  return (character === 'x' ? random : (random & 0x3 | 0x8)).toString(16)
})
const sessionId = ref(localStorage.getItem(sessionStorageKey) || createSessionId())
if (!localStorage.getItem(sessionStorageKey)) localStorage.setItem(sessionStorageKey, sessionId.value)
let speechRecognition = null

const suggestions = [
  'Fais-moi le bilan de mon ONG',
  'Quels projets sont en retard ?',
  'Résume les activités récentes',
  'Analyse les finances',
]
const voiceSupported = computed(() => typeof window !== 'undefined' && ('SpeechRecognition' in window || 'webkitSpeechRecognition' in window))

const toggleDrawer = () => {
  isOpen.value = !isOpen.value
  if (isOpen.value && !assistantData.value) {
    fetchAssistantData()
  }
}

const hasAlerts = computed(() => {
  if (!assistantData.value) return false
  return (
    (assistantData.value.alertes && assistantData.value.alertes.length > 0 && !assistantData.value.alertes[0].includes('conforme')) ||
    assistantData.value.alert === 'RED'
  )
})

const orbAnimationClasses = computed(() => {
  if (hasAlerts.value) return 'animate-pulse ring-4 ring-red-500/30'
  return ''
})

const formatMoney = (val) => {
  return new Intl.NumberFormat('fr-FR', {
    style: 'currency',
    currency: 'XOF',
    maximumFractionDigits: 0,
  }).format(val || 0)
}

const formatTime = (iso) => {
  if (!iso) return ''
  try {
    return new Date(iso).toLocaleString('fr-FR', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
    })
  } catch (e) {
    return iso
  }
}

const formatDate = (value) => {
  if (!value) return ''
  const date = new Date(value)
  return Number.isNaN(date.getTime()) ? value : date.toLocaleDateString('fr-FR')
}

const sendChat = async (suggestion = '') => {
  const question = String(suggestion || chatInput.value).trim()
  if (!question || chatLoading.value) return
  const history = messages.value.slice(-12).map(({ role, content }) => ({ role, content }))
  messages.value.push({ role: 'user', content: question })
  chatInput.value = ''
  chatLoading.value = true
  voiceError.value = ''
  await nextTick()
  chatScroll.value?.scrollTo({ top: chatScroll.value.scrollHeight, behavior: 'smooth' })
  try {
    const response = await api.post('/api/assistant/chat/', {
      question,
      history,
      session_id: sessionId.value,
    })
    if (response.data?.session_id) {
      sessionId.value = response.data.session_id
      localStorage.setItem(sessionStorageKey, sessionId.value)
    }
    messages.value.push({
      role: 'assistant',
      content: response.data?.answer || 'Je n’ai pas obtenu de réponse exploitable.',
      tool_results: response.data?.tool_results || [],
      tools_used: response.data?.tools_used || [],
      sources: response.data?.sources || [],
    })
  } catch (requestError) {
    const detail = requestError.response?.data?.detail
    messages.value.push({
      role: 'assistant',
      content: detail || 'Je ne peux pas joindre le service pour le moment. Réessayez dans quelques instants.',
    })
  } finally {
    chatLoading.value = false
    await nextTick()
    chatScroll.value?.scrollTo({ top: chatScroll.value.scrollHeight, behavior: 'smooth' })
  }
}

const restoreChat = async () => {
  if (messages.value.length || !sessionId.value) return
  try {
    const response = await api.get('/api/assistant/chat/', { params: { session_id: sessionId.value } })
    messages.value = Array.isArray(response.data?.messages) ? response.data.messages : []
    await nextTick()
    chatScroll.value?.scrollTo({ top: chatScroll.value.scrollHeight })
  } catch {
    // The next message can still resume the server-side draft by session ID.
  }
}

const toggleVoice = () => {
  if (!voiceSupported.value) {
    voiceError.value = 'La dictée vocale n’est pas prise en charge par ce navigateur.'
    return
  }
  if (voiceListening.value) {
    speechRecognition?.stop()
    return
  }
  const Recognition = window.SpeechRecognition || window.webkitSpeechRecognition
  speechRecognition = new Recognition()
  speechRecognition.lang = 'fr-FR'
  speechRecognition.interimResults = true
  speechRecognition.continuous = false
  speechRecognition.onstart = () => { voiceListening.value = true; voiceError.value = '' }
  speechRecognition.onresult = (event) => {
    const transcript = Array.from(event.results).map((result) => result[0]?.transcript || '').join(' ')
    chatInput.value = transcript.trim()
  }
  speechRecognition.onerror = () => { voiceError.value = 'La dictée a échoué. Vérifiez l’autorisation du microphone.' }
  speechRecognition.onend = () => { voiceListening.value = false }
  try { speechRecognition.start() } catch { voiceError.value = 'Le microphone est déjà utilisé.' }
}

const speak = (text) => {
  if (!('speechSynthesis' in window)) {
    voiceError.value = 'La lecture vocale n’est pas prise en charge par ce navigateur.'
    return
  }
  window.speechSynthesis.cancel()
  const utterance = new SpeechSynthesisUtterance(text)
  utterance.lang = 'fr-FR'
  window.speechSynthesis.speak(utterance)
}

const openActionRoute = (route) => {
  if (typeof route === 'string' && route.startsWith('/gerant/')) {
    isOpen.value = false
    router.push(route)
  }
}

const fetchAssistantData = async () => {
  if (!isGerant.value) return
  loading.value = true
  error.value = null
  try {
    const res = await api.get('/api/assistant/dashboard/')
    assistantData.value = res.data
  } catch (err) {
    console.error('Erreur de chargement Assistant IA:', err)
    error.value = "Impossible de récupérer les indicateurs réels depuis le serveur."
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  if (isGerant.value) {
    fetchAssistantData()
    restoreChat()
  }
})
</script>

<style scoped>
.slide-drawer-enter-active,
.slide-drawer-leave-active {
  transition: transform 0.3s cubic-bezier(0.16, 1, 0.3, 1);
}

.slide-drawer-enter-from,
.slide-drawer-leave-to {
  transform: translateX(100%);
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
