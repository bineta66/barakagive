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
          <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-sparkles"><path d="M9.937 15.5A2 2 0 0 0 8.5 14.063l-6.135-1.582a.5.5 0 0 1 0-.962L8.5 9.936A2 2 0 0 0 9.937 8.5l1.582-6.135a.5.5 0 0 1 .963 0L14.063 8.5A2 2 0 0 0 15.5 9.937l6.135 1.581a.5.5 0 0 1 0 .964L15.5 14.063a2 2 0 0 0-1.437 1.437l-1.582 6.135a.5.5 0 0 1-.963 0z"/><path d="M20 3v4"/><path d="M22 5h-4"/><path d="M4 17v2"/><path d="M5 18H3"/></svg>
        </span>
        <!-- Ping Rings -->
        <span
          v-if="orbState === 'alerte'"
          class="absolute inset-0 rounded-full border-2 border-red-500 animate-ping opacity-75"
        ></span>
        <span
          v-if="orbState === 'info'"
          class="absolute inset-0 rounded-full border-2 border-blue-500 animate-pulse opacity-50"
        ></span>
        <!-- Badge -->
        <span
          v-if="orbState === 'alerte'"
          class="absolute top-0 right-0 w-4 h-4 bg-red-600 rounded-full border-2 border-white"
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
          <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-sparkles text-or"><path d="M9.937 15.5A2 2 0 0 0 8.5 14.063l-6.135-1.582a.5.5 0 0 1 0-.962L8.5 9.936A2 2 0 0 0 9.937 8.5l1.582-6.135a.5.5 0 0 1 .963 0L14.063 8.5A2 2 0 0 0 15.5 9.937l6.135 1.581a.5.5 0 0 1 0 .964L15.5 14.063a2 2 0 0 0-1.437 1.437l-1.582 6.135a.5.5 0 0 1-.963 0z"/><path d="M20 3v4"/><path d="M22 5h-4"/><path d="M4 17v2"/><path d="M5 18H3"/></svg>
          Executive Insight IA
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
          Aucune urgence stratégique n'est détectée actuellement.
        </div>

        <template v-else>
          <!-- Résumé stratégique -->
          <div class="space-y-2">
            <h3 class="text-xs font-bold uppercase text-gray-500">Résumé stratégique</h3>
            <p class="text-sm text-bleu-nuit bg-slate-50 p-3 rounded-lg border border-slate-100">{{ insight.resume }}</p>
          </div>

          <!-- Alert State Global -->
          <div v-if="insight.alert !== 'GREEN'" class="p-3 rounded-lg bg-red-50 border border-red-100 flex items-start gap-3">
             <div class="mt-1 w-2 h-2 rounded-full bg-red-600"></div>
             <div>
               <p class="text-xs font-bold text-red-900">Alerte Stratégique</p>
               <p class="text-xs text-red-700 mt-1">L'IA a identifié des anomalies nécessitant votre attention.</p>
             </div>
          </div>

          <!-- Priority Campaign -->
          <div v-if="insight.campagne_prioritaire" class="space-y-2">
            <h3 class="text-xs font-bold uppercase text-gray-500">Campagne Prioritaire</h3>
            <div class="bg-white p-3 rounded-lg border border-slate-200 shadow-sm">
              <div class="flex justify-between items-center mb-1">
                <span class="font-semibold text-sm text-bleu-nuit">{{ insight.campagne_prioritaire.nom }}</span>
                <span class="px-2 py-0.5 rounded text-[10px] font-bold bg-orange-100 text-orange-800">
                  {{ insight.campagne_prioritaire.urgence }}
                </span>
              </div>
              <p class="text-xs text-gray-500">{{ insight.campagne_prioritaire.region }}</p>
            </div>
          </div>

          <!-- Priority Zone -->
          <div v-if="insight.zone_prioritaire" class="space-y-2">
            <h3 class="text-xs font-bold uppercase text-gray-500">Zone Prioritaire</h3>
            <div class="bg-white p-3 rounded-lg border border-slate-200 shadow-sm flex justify-between items-center">
              <div>
                <p class="font-semibold text-sm text-bleu-nuit">{{ insight.zone_prioritaire.nom }}</p>
                <p class="text-xs text-gray-500">{{ insight.zone_prioritaire.beneficiaires }} bénéficiaires</p>
              </div>
              <div class="text-right">
                <p class="text-xs text-gray-500">Score</p>
                <p class="font-bold text-or">{{ insight.zone_prioritaire.score }}</p>
              </div>
            </div>
          </div>

          <!-- Global Budget -->
          <div v-if="insight.budget" class="space-y-2">
            <h3 class="text-xs font-bold uppercase text-gray-500">Budget Global</h3>
            <div class="grid grid-cols-2 gap-2">
              <div class="bg-white p-3 rounded-lg border border-slate-200 text-center">
                <p class="text-[10px] text-gray-500 uppercase">Budget</p>
                <p class="font-semibold text-bleu-nuit">{{ formatMoney(insight.budget.total) }}</p>
              </div>
              <div class="bg-white p-3 rounded-lg border border-slate-200 text-center">
                <p class="text-[10px] text-gray-500 uppercase">Taux d'exécution</p>
                <p class="font-semibold text-bleu-nuit">{{ insight.budget.taux }}%</p>
              </div>
              <div class="bg-white p-3 rounded-lg border border-slate-200 text-center col-span-2 flex justify-between items-center">
                <div>
                  <p class="text-[10px] text-gray-500 uppercase text-left">Solde Restant</p>
                  <p class="font-semibold text-bleu-nuit">{{ formatMoney(insight.budget.solde) }}</p>
                </div>
                <span v-if="insight.budget.alerte" class="px-2 py-1 rounded bg-red-100 text-red-700 text-xs font-bold">
                  Alerte
                </span>
              </div>
            </div>
          </div>

          <!-- Recommendations -->
          <div v-if="insight.recommandations && insight.recommandations.length" class="space-y-2">
            <h3 class="text-xs font-bold uppercase text-gray-500">Recommandations IA</h3>
            <ul class="space-y-2">
              <li v-for="(rec, idx) in insight.recommandations.slice(0, 3)" :key="idx" class="flex gap-2 items-start bg-slate-50 p-2 rounded border border-slate-100">
                <span class="text-or text-xs mt-0.5 font-bold">{{ idx + 1 }}.</span>
                <span class="text-sm text-bleu-nuit">{{ rec }}</span>
              </li>
            </ul>
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
import api from '@/services/api'

const isOpen = ref(false)
const loading = ref(false)
const insight = ref(null)

const toggleDrawer = () => {
  isOpen.value = !isOpen.value
  if (isOpen.value && !insight.value) {
    fetchInsight()
  }
}

const orbState = computed(() => {
  if (!insight.value) return 'normal'
  if (insight.value.alert === 'RED') return 'alerte'
  if (insight.value.alert === 'YELLOW' || insight.value.alert === 'ORANGE') return 'info'
  return 'normal'
})

const orbAnimationClasses = computed(() => {
  if (orbState.value === 'alerte') return 'animate-pulse ring-4 ring-red-500/30'
  return ''
})

const formatMoney = (val) => {
  return new Intl.NumberFormat('fr-FR', { style: 'currency', currency: 'XOF' }).format(val || 0)
}

const formatTime = (iso) => {
  if (!iso) return ''
  return new Date(iso).toLocaleString('fr-FR')
}

const fetchInsight = async () => {
  loading.value = true
  try {
    const res = await api.get('/api/ia/executive-insight')
    insight.value = res.data
  } catch (error) {
    console.error('Failed to load Executive Insight', error)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchInsight()
})
</script>
