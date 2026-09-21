<template>
  <div v-if="isGerant">
    <!-- Floating Orb (Visible uniquement pour le Gérant) -->
    <div
      class="fixed bottom-6 right-6 z-50 cursor-pointer transition-transform duration-300 hover:scale-110 select-none group"
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
          class="absolute inset-0 rounded-full border-2 border-red-500 animate-ping opacity-60 pointer-events-none"
        ></span>
        <span
          v-else
          class="absolute inset-0 rounded-full border border-[#CCA43B] animate-pulse opacity-40 pointer-events-none"
        ></span>

        <!-- Alert Counter Badge -->
        <span
          v-if="hasAlerts"
          class="absolute -top-1 -right-1 flex h-5 w-5 items-center justify-center rounded-full bg-red-600 text-[10px] font-bold text-white shadow-md border-2 border-[#021B30]"
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

          <div class="flex items-center gap-2">
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
        <div class="p-6 flex-1 overflow-y-auto space-y-6">
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
            <div class="grid grid-cols-3 gap-3">
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
                <span class="w-1.5 h-1.5 rounded-full bg-blue-500"></span>
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
import { ref, computed, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import api from '@/services/api'

const authStore = useAuthStore()
const isGerant = computed(() => authStore.role === 'GERANT')

const isOpen = ref(false)
const loading = ref(false)
const error = ref(null)
const assistantData = ref(null)

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
