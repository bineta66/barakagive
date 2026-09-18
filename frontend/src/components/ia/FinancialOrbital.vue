<template>
  <div>
    <!-- Floating Orb -->
    <div
      class="fixed bottom-6 right-6 z-50 cursor-pointer transition-transform duration-300 hover:scale-110"
      @click="toggleDrawer"
    >
      <div
        class="relative flex items-center justify-center w-16 h-16 rounded-full bg-white/80 backdrop-blur-md shadow-lg border border-white/50"
        :class="orbAnimationClasses"
      >
        <span class="text-or">
          <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-banknote"><rect width="20" height="12" x="2" y="6" rx="2"/><circle cx="12" cy="12" r="2"/><path d="M6 12h.01M18 12h.01"/></svg>
        </span>
        <!-- Rings and Badges based on state -->
        <span
          v-if="orbState === 'RED'"
          class="absolute inset-0 rounded-full border-2 border-red-500 animate-spin opacity-75"
        ></span>
        <span
          v-if="orbState === 'ORANGE'"
          class="absolute inset-0 rounded-full border-2 border-orange-500 animate-ping opacity-50"
        ></span>
        <span
          v-if="orbState === 'YELLOW'"
          class="absolute inset-0 rounded-full border-2 border-yellow-500 opacity-50"
        ></span>
        <!-- Badges -->
        <span
          v-if="orbState === 'RED' || orbState === 'YELLOW'"
          class="absolute top-0 right-0 w-4 h-4 rounded-full border-2 border-white"
          :class="badgeColorClass"
        ></span>
      </div>
    </div>

    <!-- Drawer -->
    <div
      v-if="isOpen"
      class="fixed inset-y-0 right-0 z-[60] w-96 bg-white/90 backdrop-blur-xl shadow-2xl border-l border-white/50 transform transition-transform duration-300 ease-in-out flex flex-col"
      :class="isOpen ? 'translate-x-0' : 'translate-x-full'"
    >
      <div class="p-6 border-b border-slate-100 flex justify-between items-center bg-white/50">
        <h2 class="text-xl font-bold text-bleu-nuit flex items-center gap-2">
          <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-banknote text-or"><rect width="20" height="12" x="2" y="6" rx="2"/><circle cx="12" cy="12" r="2"/><path d="M6 12h.01M18 12h.01"/></svg>
          Financial Orbital
        </h2>
        <button @click="toggleDrawer" class="text-gray-400 hover:text-gray-600">
          <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M18 6 6 18"/><path d="m6 6 12 12"/></svg>
        </button>
      </div>

      <div class="p-6 flex-1 overflow-y-auto space-y-6">
        <div v-if="loading" class="flex justify-center items-center h-32">
          <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-or"></div>
        </div>
        
        <div v-else-if="!insight" class="text-sm text-gray-500 italic">
          Les dépenses restent cohérentes avec le budget prévu. Aucun risque financier n'est détecté pour le moment.
        </div>

        <template v-else>
          <!-- Alert Level -->
          <div class="p-3 rounded-lg flex items-center gap-3 border" :class="alertBoxClass">
             <div class="w-3 h-3 rounded-full" :class="alertDotClass"></div>
             <div>
               <p class="text-xs font-bold uppercase">{{ insight.alert }}</p>
               <p class="text-xs mt-0.5">{{ insight.resume }}</p>
             </div>
          </div>

          <!-- Budget overview -->
          <div class="grid grid-cols-2 gap-2">
            <div class="bg-slate-50 p-3 rounded-lg border border-slate-100">
              <p class="text-[10px] text-gray-500 uppercase">Budget Total</p>
              <p class="font-bold text-bleu-nuit">{{ formatMoney(insight.budget) }}</p>
            </div>
            <div class="bg-slate-50 p-3 rounded-lg border border-slate-100">
              <p class="text-[10px] text-gray-500 uppercase">Dépenses</p>
              <p class="font-bold text-or">{{ formatMoney(insight.depenses) }}</p>
            </div>
            <div class="bg-slate-50 p-3 rounded-lg border border-slate-100">
              <p class="text-[10px] text-gray-500 uppercase">Solde</p>
              <p class="font-bold text-bleu-nuit">{{ formatMoney(insight.solde) }}</p>
            </div>
            <div class="bg-slate-50 p-3 rounded-lg border border-slate-100">
              <p class="text-[10px] text-gray-500 uppercase">Taux d'exécution</p>
              <p class="font-bold text-bleu-nuit">{{ insight.taux_execution }}%</p>
            </div>
          </div>

          <!-- Timeline -->
          <div class="space-y-2">
             <div class="flex justify-between items-center bg-white p-3 rounded-lg border border-slate-200 shadow-sm">
                <div>
                  <p class="text-xs text-gray-500">Date de clôture</p>
                  <p class="text-sm font-semibold text-bleu-nuit">{{ insight.date_cloture }}</p>
                </div>
                <div class="text-right">
                  <p class="text-xs text-gray-500">Jours restants</p>
                  <p class="text-sm font-bold text-or">{{ insight.jours_restants }} j</p>
                </div>
             </div>
          </div>

          <!-- Insights -->
          <div class="space-y-2">
            <div class="bg-white p-3 rounded-lg border border-slate-200 text-sm">
               <div class="flex justify-between mb-2">
                  <span class="text-gray-500">Zone la plus dépensière</span>
                  <span class="font-semibold text-bleu-nuit">{{ insight.zone_plus_depensiere }}</span>
               </div>
               <div class="flex justify-between">
                  <span class="text-gray-500">Catégorie la plus dépensière</span>
                  <span class="font-semibold text-bleu-nuit">{{ insight.categorie_plus_depensiere }}</span>
               </div>
            </div>
          </div>

          <!-- Predictions & Recommandations -->
          <div class="space-y-4">
            <div>
               <h3 class="text-xs font-bold uppercase text-gray-500 mb-1">Prédiction IA</h3>
               <p class="text-sm text-gray-800 bg-blue-50 p-3 rounded-lg border border-blue-100">{{ insight.prediction }}</p>
            </div>
            <div>
               <h3 class="text-xs font-bold uppercase text-gray-500 mb-1">Justification</h3>
               <p class="text-sm text-gray-800">{{ insight.justification }}</p>
            </div>
            <div>
               <h3 class="text-xs font-bold uppercase text-gray-500 mb-1">Recommandation</h3>
               <p class="text-sm font-semibold text-bleu-nuit bg-slate-50 p-3 rounded-lg border border-slate-200">{{ insight.recommandation }}</p>
            </div>
          </div>
          
          <p class="text-[10px] text-gray-400 mt-4">Généré le {{ formatTime(insight.generated_at) }}</p>
        </template>
      </div>
    </div>
    
    <!-- Backdrop overlay -->
    <div
      v-if="isOpen"
      @click="toggleDrawer"
      class="fixed inset-0 bg-black/10 z-[55] backdrop-blur-sm"
    ></div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import api from '@/services/api.js'

const isOpen = ref(false)
const loading = ref(false)
const insight = ref(null)
const activeCampaignId = ref(null)

const authStore = useAuthStore()

const toggleDrawer = () => {
  isOpen.value = !isOpen.value
  if (isOpen.value && !insight.value) {
    fetchInsight()
  }
}

const orbState = computed(() => {
  if (!insight.value || insight.value.alert === 'GREEN') return 'GREEN'
  return insight.value.alert || 'GREEN'
})

const orbAnimationClasses = computed(() => {
  if (orbState.value === 'RED') return 'animate-pulse ring-4 ring-red-500/30'
  if (orbState.value === 'ORANGE') return 'animate-pulse ring-4 ring-orange-500/30'
  return ''
})

const badgeColorClass = computed(() => {
  if (orbState.value === 'RED') return 'bg-red-600'
  if (orbState.value === 'YELLOW') return 'bg-yellow-400'
  return ''
})

const alertBoxClass = computed(() => {
  if (orbState.value === 'RED') return 'bg-red-50 border-red-200 text-red-900'
  if (orbState.value === 'ORANGE') return 'bg-orange-50 border-orange-200 text-orange-900'
  if (orbState.value === 'YELLOW') return 'bg-yellow-50 border-yellow-200 text-yellow-900'
  return 'bg-green-50 border-green-200 text-green-900'
})

const alertDotClass = computed(() => {
  if (orbState.value === 'RED') return 'bg-red-600'
  if (orbState.value === 'ORANGE') return 'bg-orange-500'
  if (orbState.value === 'YELLOW') return 'bg-yellow-400'
  return 'bg-green-500'
})

const formatMoney = (val) => {
  return new Intl.NumberFormat('fr-FR', { style: 'currency', currency: 'XOF' }).format(val || 0)
}

const formatTime = (iso) => {
  if (!iso) return ''
  return new Date(iso).toLocaleString('fr-FR')
}

const fetchInsight = async () => {
  // First, get the active campaign for the user's organization
  if (!activeCampaignId.value) {
    await fetchActiveCampaign()
  }
  
  if (!activeCampaignId.value) {
    // No active campaign found
    insight.value = null
    return
  }
  
  loading.value = true
  try {
    const res = await api.get(`/api/ia/budget-analysis/${activeCampaignId.value}/`)
    insight.value = res.data
  } catch (error) {
    console.error('Failed to load Financial Insight', error)
    insight.value = null
  } finally {
    loading.value = false
  }
}

const fetchActiveCampaign = async () => {
  try {
    const res = await api.get('/api/campaigns/')
    const campaigns = res.data || []
    // Find first active campaign
    const active = campaigns.find(c => c.statut === 'EN_COURS' || c.statut === 'ACTIVE')
    if (active) {
      activeCampaignId.value = active.id
    }
  } catch (error) {
    console.error('Failed to fetch active campaign', error)
  }
}

onMounted(() => {
  fetchActiveCampaign()
})
</script>