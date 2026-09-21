<template>
  <div v-if="selectedRegion" class="mt-6 space-y-4 animate-fade-in">
    <div class="flex items-center justify-between">
      <h3 class="text-lg font-bold text-or flex items-center gap-2">
        <MapPin :size="20" />
        Zones prioritaires IA — {{ selectedRegion }}
      </h3>
      <span class="px-3 py-1 bg-bleu-nuit/10 text-bleu-nuit text-xs font-semibold rounded-full">
        {{ zones.length }} zone(s)
      </span>
    </div>

    <div v-if="loading" class="flex justify-center items-center py-8">
      <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-or"></div>
    </div>

    <div v-else-if="error" class="p-4 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm">
      {{ error }}
    </div>

    <div v-else-if="zones.length === 0" class="p-6 bg-slate-50 border border-slate-200 rounded-xl text-center">
      <p class="text-sm text-gray-500">
        Aucune zone prioritaire n'est détectée actuellement. Continuez la collecte des données.
      </p>
    </div>

    <div v-else class="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
      <ZoneAnalysisCard
        v-for="zone in zones"
        :key="zone.zone_id || zone.id"
        :zone="zone"
        :rang="zones.indexOf(zone) + 1"
      />
    </div>

    <!-- Bouton pour voir l'analyse IA complète de la région -->
    <div class="mt-4 text-center">
      <BoutonPrimary 
        class="w-full sm:w-auto"
        @click="goToRegionAnalysis"
      >
        <Brain :size="18" class="mr-2" />
        Voir l'analyse IA complète de la région
      </BoutonPrimary>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from "vue"
import { MapPin, Brain } from "lucide-vue-next"
import { useRouter } from "vue-router"
import api from "@/services/api.js"
import ZoneAnalysisCard from "./ZoneAnalysisCard.vue"
import BoutonPrimary from "@/components/ui/BoutonPrimary.vue"

const props = defineProps({
  selectedRegion: {
    type: String,
    default: "",
  },
})

const router = useRouter()

const zones = ref([])
const loading = ref(false)
const error = ref(null)

const fetchZonesForRegion = async () => {
  if (!props.selectedRegion) {
    zones.value = []
    return
  }

  loading.value = true
  error.value = null

  try {
    // Call the Django endpoint for computed zone scores
    const response = await api.get(`/api/ia/regions/${encodeURIComponent(props.selectedRegion)}/analysis`)
    zones.value = response.data.zones || []
  } catch (err) {
    error.value = err.response?.data?.detail || "Impossible de charger les zones prioritaires."
    zones.value = []
  } finally {
    loading.value = false
  }
}

watch(
  () => props.selectedRegion,
  () => {
    fetchZonesForRegion()
  },
  { immediate: true }
)

const goToRegionAnalysis = () => {
  router.push(`/chef-projet/zones/analyse-region/${encodeURIComponent(props.selectedRegion)}`)
}
</script>