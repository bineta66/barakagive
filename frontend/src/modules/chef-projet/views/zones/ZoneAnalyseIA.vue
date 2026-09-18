<template>
  <div class="p-6 space-y-6 bg-white min-h-screen">
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-3xl font-bold text-or">Analyse de zone IA</h1>
        <p class="text-sm text-gray-500 mt-1">
          Détail de l'analyse prioritaire pour la zone sélectionnée.
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

    <div v-else-if="zone" class="space-y-6">
      <!-- Header -->
      <div class="bg-white border border-slate-200/60 rounded-xl p-6 shadow-sm">
        <div class="flex items-center justify-between mb-4">
          <div>
            <h2 class="text-2xl font-bold text-bleu-nuit">{{ zone.nom }}</h2>
            <p class="text-sm text-gray-500 mt-1">{{ zone.region }} · {{ zone.departement }}</p>
          </div>
          <span
            class="px-4 py-2 rounded-lg text-sm font-semibold"
            :class="urgencyClass"
          >
            {{ zone.niveau }}
          </span>
        </div>

        <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div class="bg-slate-50 p-4 rounded-lg text-center">
            <p class="text-[10px] text-gray-500 uppercase">Score Total IA</p>
            <p class="font-bold text-3xl text-or mt-1">{{ zone.score_total.toFixed(1) }}</p>
          </div>
          <div class="bg-slate-50 p-4 rounded-lg text-center">
            <p class="text-[10px] text-gray-500 uppercase">Bénéficiaires</p>
            <p class="font-bold text-3xl text-bleu-nuit mt-1">{{ zone.beneficiaires }}</p>
          </div>
          <div class="bg-slate-50 p-4 rounded-lg text-center">
            <p class="text-[10px] text-gray-500 uppercase">Région</p>
            <p class="font-bold text-bleu-nuit mt-1">{{ zone.region }}</p>
          </div>
          <div class="bg-slate-50 p-4 rounded-lg text-center">
            <p class="text-[10px] text-gray-500 uppercase">Département</p>
            <p class="font-bold text-bleu-nuit mt-1">{{ zone.departement }}</p>
          </div>
        </div>
      </div>

      <!-- Justification IA -->
      <div class="bg-white border border-slate-200/60 rounded-xl p-6 shadow-sm">
        <h3 class="text-lg font-bold text-bleu-nuit mb-3 flex items-center gap-2">
          <MessageSquare :size="20" />
          Justification IA
        </h3>
        <p class="text-gray-700 whitespace-pre-line">{{ zone.justification }}</p>
      </div>

      <!-- Recommandation IA -->
      <div class="bg-white border border-slate-200/60 rounded-xl p-6 shadow-sm">
        <h3 class="text-lg font-bold text-bleu-nuit mb-3 flex items-center gap-2">
          <Lightbulb :size="20" class="text-or" />
          Recommandation IA
        </h3>
        <p class="font-semibold text-bleu-nuit bg-slate-50 p-4 rounded-lg border border-slate-200">
          {{ zone.recommandation }}
        </p>
      </div>

      <!-- Top 5 Bénéficiaires -->
      <div v-if="zone.top5_beneficiaires && zone.top5_beneficiaires.length" class="bg-white border border-slate-200/60 rounded-xl p-6 shadow-sm">
        <h3 class="text-lg font-bold text-bleu-nuit mb-4 flex items-center gap-2">
          <Users :size="20" />
          Top 5 bénéficiaires les plus vulnérables
        </h3>
        <div class="overflow-x-auto">
          <table class="w-full">
            <thead>
              <tr class="text-left text-xs font-bold uppercase text-gray-500 border-b border-slate-200">
                <th class="pb-2">Rang</th>
                <th class="pb-2">Nom</th>
                <th class="pb-2">Prénom</th>
                <th class="pb-2">Score IA</th>
                <th class="pb-2">Vulnérabilité</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(b, idx) in zone.top5_beneficiaires" :key="idx" class="border-b border-slate-100">
                <td class="py-3 font-semibold text-bleu-nuit">{{ idx + 1 }}</td>
                <td class="py-3 text-gray-700">{{ b.nom }}</td>
                <td class="py-3 text-gray-700">{{ b.prenom }}</td>
                <td class="py-3 font-bold text-or">{{ b.score }}</td>
                <td class="py-3">
                  <span
                    class="px-2 py-1 rounded text-xs font-semibold"
                    :class="vulnClass(b.vulnerabilite)"
                  >
                    {{ b.vulnerabilite }}
                  </span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <p class="text-[10px] text-gray-400 text-center">
        Généré le {{ formatTime(zone.generated_at) }}
      </p>
    </div>

    <div v-else class="text-center py-12 text-gray-500">
      Aucune donnée disponible pour cette zone.
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue"
import { useRoute, useRouter } from "vue-router"
import { ArrowLeft, MessageSquare, Lightbulb, Users } from "lucide-vue-next"
import BoutonSecondary from "@/components/ui/BoutonSecondary.vue"
import LoadingSpinner from "@/components/ui/LoadingSpinner.vue"
import api from "@/services/api.js"

const route = useRoute()
const router = useRouter()

const zone = ref(null)
const loading = ref(true)
const error = ref(null)

const urgencyClass = computed(() => {
  switch (zone.value?.niveau) {
    case "Très élevée":
    case "Critique":
      return "bg-red-100 text-red-700"
    case "Élevée":
      return "bg-orange-100 text-orange-700"
    case "Moyenne":
      return "bg-yellow-100 text-yellow-700"
    default:
      return "bg-green-100 text-green-700"
  }
})

const vulnClass = (v) => {
  switch (v) {
    case "Critique":
      return "bg-red-100 text-red-700"
    case "Élevée":
      return "bg-orange-100 text-orange-700"
    case "Moyenne":
      return "bg-yellow-100 text-yellow-700"
    default:
      return "bg-green-100 text-green-700"
  }
}

const formatTime = (iso) => {
  if (!iso) return ""
  return new Date(iso).toLocaleString("fr-FR")
}

const fetchZoneDetail = async () => {
  loading.value = true
  error.value = null
  try {
    const response = await api.get(`/api/ia/zones/${route.params.id}`)
    zone.value = response.data
  } catch (err) {
    error.value = err.response?.data?.detail || "Impossible de charger l'analyse de zone."
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchZoneDetail()
})
</script>