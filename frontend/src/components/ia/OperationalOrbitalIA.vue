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
          <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-map-pin"><path d="M20 10c0 4.993-5.539 10.193-7.399 11.799a1 1 0 0 1-1.202 0C9.539 20.193 4 14.993 4 10a8 8 0 0 1 16 0"/><circle cx="12" cy="10" r="3"/></svg>
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
        <span
          v-if="orbState === 'info'"
          class="absolute top-0 right-0 w-4 h-4 bg-blue-600 rounded-full border-2 border-white"
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
          <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-map-pin text-or"><path d="M20 10c0 4.993-5.539 10.193-7.399 11.799a1 1 0 0 1-1.202 0C9.539 20.193 4 14.993 4 10a8 8 0 0 1 16 0"/><circle cx="12" cy="10" r="3"/></svg>
          Assistant Opérationnel IA
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
          Aucune zone prioritaire n'est détectée actuellement. Continuez la collecte des données afin d'obtenir une analyse plus précise.
        </div>

        <template v-else>
          <!-- 1. Résumé de la campagne -->
          <div class="space-y-2">
            <h3 class="text-xs font-bold uppercase text-gray-500">Résumé de la campagne</h3>
            <p class="text-sm text-bleu-nuit bg-slate-50 p-3 rounded-lg border border-slate-100">
              {{ insight.resume_campagne || "Aucune campagne active détectée." }}
            </p>
          </div>

          <!-- 2. Zone prioritaire -->
          <div v-if="zone_prioritaire" class="space-y-2">
            <h3 class="text-xs font-bold uppercase text-gray-500">Zone prioritaire</h3>
            <div class="bg-white p-3 rounded-lg border border-slate-200 shadow-sm space-y-1">
              <div class="flex justify-between">
                <span class="text-xs text-gray-500">Région</span>
                <span class="font-semibold text-sm text-bleu-nuit">{{ zone_prioritaire.region }}</span>
              </div>
              <div class="flex justify-between">
                <span class="text-xs text-gray-500">Zone</span>
                <span class="font-semibold text-sm text-bleu-nuit">{{ zone_prioritaire.nom }}</span>
              </div>
              <div class="flex justify-between">
                <span class="text-xs text-gray-500">Urgence</span>
                <span class="px-2 py-0.5 rounded text-[10px] font-bold" :class="urgencyBadgeClass(zone_prioritaire.niveau_urgence)">
                  {{ zone_prioritaire.niveau_urgence }}
                </span>
              </div>
              <div class="flex justify-between">
                <span class="text-xs text-gray-500">Score total</span>
                <span class="font-bold text-or text-sm">{{ zone_prioritaire.score_total }}</span>
              </div>
              <div class="flex justify-between">
                <span class="text-xs text-gray-500">Bénéficiaires</span>
                <span class="font-semibold text-sm text-bleu-nuit">{{ zone_prioritaire.beneficiaires }}</span>
              </div>
            </div>
          </div>

          <!-- 3. Décision IA -->
          <div v-if="insight.decision_ia" class="space-y-2">
            <h3 class="text-xs font-bold uppercase text-gray-500">Décision IA</h3>
            <p class="text-sm text-bleu-nuit bg-slate-50 p-3 rounded-lg border border-slate-100 italic">
              {{ insight.decision_ia }}
            </p>
          </div>

          <!-- 4. Recommandations terrain -->
          <div v-if="insight.recommandations && insight.recommandations.length" class="space-y-2">
            <h3 class="text-xs font-bold uppercase text-gray-500">Recommandations terrain</h3>
            <ul class="space-y-1">
              <li v-for="(rec, idx) in insight.recommandations.slice(0, 3)" :key="idx" class="flex items-start gap-2 text-sm text-gray-700">
                <span class="text-or mt-1">•</span>
                <span>{{ rec }}</span>
              </li>
            </ul>
          </div>

          <!-- 5. Régions → Zones (link to existing zone analysis) -->
          <div class="space-y-2 pt-4 border-t border-slate-100">
            <h3 class="text-xs font-bold uppercase text-gray-500">Analyse détaillée par région</h3>
            <p class="text-xs text-gray-500 mb-2">Cliquez sur une région dans la carte des zones pour voir le classement IA.</p>
            <BoutonPrimary 
              to="/chef-projet/zones/carte" 
              class="w-full text-sm"
            >
              <MapPin :size="16" />
              Voir la carte des zones
            </BoutonPrimary>
          </div>

          <p class="text-[10px] text-gray-400 pt-4 border-t border-slate-100">
            Généré le {{ formatTime(insight.generated_at) }}
          </p>
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
import { useRouter } from 'vue-router'
import { MapPin } from 'lucide-vue-next'
import api from '@/services/api.js'
import BoutonPrimary from '@/components/ui/BoutonPrimary.vue'

const router = useRouter()

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
  if (!insight.zone_prioritaire) return 'normal'
  const urgence = insight.value.zone_prioritaire?.niveau_urgence || ''
  if (urgence === 'Très élevée' || urgence === 'Critique') return 'alerte'
  if (urgence === 'Élevée') return 'info'
  return 'normal'
})

const orbAnimationClasses = computed(() => {
  if (orbState.value === 'alerte') return 'animate-pulse ring-4 ring-red-500/30'
  if (orbState.value === 'info') return 'animate-pulse ring-4 ring-blue-500/30'
  return ''
})

const urgencyBadgeClass = (urgence) => {
  switch (urgence) {
    case 'Très élevée':
    case 'Critique':
      return 'bg-red-100 text-red-700'
    case 'Élevée':
      return 'bg-orange-100 text-orange-700'
    case 'Moyenne':
      return 'bg-yellow-100 text-yellow-700'
    default:
      return 'bg-green-100 text-green-700'
  }
}

const zone_prioritaire = computed(() => {
  return insight.value?.zone_prioritaire || null
})

const formatTime = (iso) => {
  if (!iso) return ''
  return new Date(iso).toLocaleString('fr-FR')
}

const fetchInsight = async () => {
  loading.value = true
  try {
    // Get the active campaign first
    const campaignsRes = await api.get('/api/campaigns/')
    const campaigns = campaignsRes.data || []
    const activeCampaign = campaigns.find(c => c.statut === 'EN_COURS' || c.statut === 'ACTIVE')
    
    if (!activeCampaign) {
      insight.value = null
      return
    }

    // Get executive insight which contains campaign summary and priority zone
    const executiveRes = await api.get('/api/ia/executive-insight')
    insight.value = executiveRes.data
  } catch (error) {
    console.error('Failed to load Operational Insight', error)
    insight.value = null
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchInsight()
})
</script>