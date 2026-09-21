<template>
  <div class="p-6 space-y-6 bg-white min-h-screen">
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-3xl font-bold text-or">Analyse de la région</h1>
        <p class="text-sm text-gray-500 mt-1">
          Analyse IA des zones prioritaires pour la région sélectionnée.
        </p>
      </div>
      <BoutonSecondary to="/chef-projet/zones/carte">
        <ArrowLeft :size="18" />
        Retour à la carte
      </BoutonSecondary>
    </div>

    <LoadingSpinner v-if="loading" message="Chargement de l'analyse..." />

    <div v-else-if="error" class="p-6 bg-red-50 border border-red-200 rounded-xl text-red-700">
      {{ error }}
    </div>

    <div v-else-if="analysis" class="space-y-6">
      <!-- Executive Summary -->
      <div class="bg-white border border-slate-200/60 rounded-xl p-6 shadow-sm">
        <h2 class="text-xl font-bold text-bleu-nuit mb-4 flex items-center gap-2">
          <FileText :size="22" />
          Résumé exécutif
        </h2>
        <p class="text-gray-700 whitespace-pre-line text-lg leading-relaxed">{{ analysis.executive_summary }}</p>
        <p class="text-[11px] text-gray-400 text-right mt-3">
          Généré le {{ formatTime(analysis.generated_at) }}
        </p>
      </div>

      <!-- Zones classées par priorité -->
      <div class="bg-white border border-slate-200/60 rounded-xl p-6 shadow-sm">
        <h2 class="text-xl font-bold text-bleu-nuit mb-4 flex items-center gap-2">
          <ArrowUpDown :size="22" />
          Zones classées par priorité
        </h2>

        <div v-if="analysis.zone_analysis && analysis.zone_analysis.length" class="space-y-4">
          <div 
            v-for="(zoneAnalysis, index) in analysis.zone_analysis" 
            :key="index"
            class="border border-slate-200 rounded-xl p-5 bg-slate-50/50 transition-all hover:shadow-md"
          >
            <div class="flex items-start gap-4">
              <!-- Rang + Zone Name + Score -->
              <div class="flex items-center gap-3 flex-shrink-0">
                <span 
                  class="w-10 h-10 rounded-full bg-bleu-nuit text-white font-bold text-lg flex items-center justify-center"
                >
                  {{ index + 1 }}
                </span>
                <div>
                  <h3 class="font-bold text-bleu-nuit text-lg">{{ zoneAnalysis.zone }}</h3>
                  <p class="text-sm text-gray-500">{{ getZoneScore(zoneAnalysis.zone) }} / 100</p>
                </div>
              </div>

              <!-- Beneficiaries + Level -->
              <div class="flex-1 flex items-center justify-between md:ml-4">
                <div class="flex items-center gap-3 text-sm text-gray-600">
                  <span class="flex items-center gap-1">
                    <Users :size="16" />
                    {{ getZoneBeneficiaries(zoneAnalysis.zone) }} bénéficiaires
                  </span>
                  <span 
                    :class="getLevelClass(getZoneLevel(zoneAnalysis.zone))"
                    class="px-3 py-1 rounded-full text-xs font-semibold"
                  >
                    {{ getLevelLabel(getZoneLevel(zoneAnalysis.zone)) }}
                  </span>
                </div>
              </div>
            </div>

            <!-- IA Summary -->
            <div class="mt-4 pt-4 border-t border-slate-200">
              <p class="text-gray-700 leading-relaxed">{{ zoneAnalysis.summary }}</p>
            </div>
          </div>
        </div>

        <div v-else class="text-center py-8 text-gray-500">
          Aucune zone trouvée pour cette région.
        </div>
      </div>

      <!-- Recommandations -->
      <div class="bg-white border border-slate-200/60 rounded-xl p-6 shadow-sm">
        <h2 class="text-xl font-bold text-bleu-nuit mb-4 flex items-center gap-2">
          <Lightbulb :size="22" class="text-or" />
          Recommandations
        </h2>

        <div v-if="analysis.recommendations && analysis.recommendations.length" class="space-y-3">
          <div 
            v-for="(rec, index) in analysis.recommendations" 
            :key="index"
            class="flex items-start gap-3 p-4 bg-slate-50 border border-slate-200 rounded-lg"
          >
            <span class="w-6 h-6 rounded-full bg-or text-white text-xs font-bold flex items-center justify-center flex-shrink-0 mt-0.5">
              {{ index + 1 }}
            </span>
            <p class="text-gray-700 leading-relaxed">{{ rec }}</p>
          </div>
        </div>

        <div v-else class="text-center py-4 text-gray-500">
          Aucune recommandation disponible.
        </div>
      </div>
    </div>

    <div v-else class="text-center py-12 text-gray-500">
      Aucune donnée disponible pour cette région.
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from "vue"
import { useRoute, useRouter } from "vue-router"
import { ArrowLeft, FileText, ArrowUpDown, Users, Lightbulb } from "lucide-vue-next"
import BoutonSecondary from "@/components/ui/BoutonSecondary.vue"
import LoadingSpinner from "@/components/ui/LoadingSpinner.vue"
import api from "@/services/api.js"

const route = useRoute()
const router = useRouter()

const analysis = ref(null)
const loading = ref(true)
const error = ref(null)

const regionName = computed(() => route.params.region)

const formatTime = (iso) => {
  if (!iso) return ""
  return new Date(iso).toLocaleString("fr-FR")
}

const getZoneScore = (zoneName) => {
  // This will be populated from zonesData
  const zone = zonesData.value.find(z => z.name === zoneName)
  return zone ? zone.score : 0
}

const getZoneBeneficiaries = (zoneName) => {
  const zone = zonesData.value.find(z => z.name === zoneName)
  return zone ? zone.beneficiaries : 0
}

const getZoneLevel = (zoneName) => {
  const zone = zonesData.value.find(z => z.name === zoneName)
  return zone ? zone.level : "FAIBLE"
}

const getLevelClass = (level) => {
  switch (level) {
    case "TRES_ELEVEE":
      return "bg-red-100 text-red-700"
    case "ELEVEE":
      return "bg-orange-100 text-orange-700"
    case "MOYENNE":
      return "bg-yellow-100 text-yellow-700"
    case "FAIBLE":
      return "bg-green-100 text-green-700"
    default:
      return "bg-gray-100 text-gray-700"
  }
}

const getLevelLabel = (level) => {
  switch (level) {
    case "TRES_ELEVEE":
      return "Très élevée"
    case "ELEVEE":
      return "Élevée"
    case "MOYENNE":
      return "Moyenne"
    case "FAIBLE":
      return "Faible"
    case "AUCUNE_DONNEE":
      return "Aucune donnée"
    default:
      return level
  }
}

const zonesData = ref([])

const fetchRegionAnalysis = async () => {
  loading.value = true
  error.value = null
  try {
    // First, get the zones data with scores from Django
    const zonesResponse = await api.get(`/api/ia/regions/${encodeURIComponent(regionName.value)}/analysis`)
    zonesData.value = zonesResponse.data.zones || []
    
    // Then, trigger IA analysis
    const iaResponse = await api.post(`/api/ia/regions/${encodeURIComponent(regionName.value)}/analyze`, zonesResponse.data)
    analysis.value = iaResponse.data
  } catch (err) {
    error.value = err.response?.data?.detail || "Impossible de charger l'analyse de la région."
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchRegionAnalysis()
})
</script>