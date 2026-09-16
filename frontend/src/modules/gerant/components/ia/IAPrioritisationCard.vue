<template>
  <div class="bg-white border border-slate-200/60 rounded-xl p-6 shadow-xs-sm">
    <div class="flex items-center justify-between mb-4">
      <div>
        <h2 class="text-base font-bold text-slate-900">Analyse de priorisation IA</h2>
        <p class="text-xs text-gray-500 mt-1">
          Synthèse générée à partir des données de la campagne.
        </p>
      </div>
      <button
        @click="evaluate"
        :disabled="loading"
        class="px-3 py-2 bg-bleu-nuit text-white text-xs font-semibold rounded-lg hover:bg-[#01111eff] disabled:opacity-50 transition"
      >
        Évaluer
      </button>
    </div>

    <div v-if="loading" class="flex items-center gap-2 text-xs text-gray-500">
      <span class="inline-block w-4 h-4 border-2 border-bleu-nuit border-t-transparent rounded-full animate-spin"></span>
      Analyse en cours...
    </div>

    <div v-else-if="error" class="text-xs text-red-600">
      {{ error }}
    </div>

    <div v-else-if="data" class="space-y-3 text-sm text-gray-700">
      <p class="font-semibold text-slate-900">Résumé</p>
      <p>{{ data.resume }}</p>

      <div class="grid grid-cols-1 sm:grid-cols-3 gap-3">
        <div class="p-3 rounded-lg border border-slate-100">
          <p class="text-xs text-gray-500">Zone recommandée</p>
          <p class="text-sm font-semibold text-slate-900">{{ data.zone_recommandee }}</p>
        </div>
        <div class="p-3 rounded-lg border border-slate-100 sm:col-span-2">
          <p class="text-xs text-gray-500">Justification</p>
          <p class="text-sm font-semibold text-slate-900">{{ data.justification }}</p>
        </div>
      </div>

      <p class="text-xs text-gray-500">
        Généré le {{ generatedAt }}
      </p>
    </div>

    <div v-else class="text-xs text-gray-500">
      Appuyez sur Évaluer pour générer l’analyse de priorisation IA.
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from "vue"
import api from "@/services/api.js"

const props = defineProps({
  campagneId: {
    type: [String, Number],
    default: null,
  },
  projetId: {
    type: [String, Number],
    default: null,
  },
  zones: {
    type: Array,
    default: () => [],
  },
})

const loading = ref(false)
const error = ref(null)
const data = ref(null)

const generatedAt = computed(() => {
  if (!data.value?.generated_at) return ""
  return new Date(data.value.generated_at).toLocaleString("fr-FR")
})

const evaluate = async () => {
  if (!props.campagneId || !props.projetId) return
  loading.value = true
  error.value = null
  data.value = null
  try {
    const response = await api.post("/api/ia/priorisation", {
      campagne: {
        id: String(props.campagneId),
        nom: "Campagne",
        statut: "ACTIVE",
      },
      projet: {
        id: String(props.projetId),
        nom: "Projet",
      },
      zones: props.zones.map((zone) => ({
        nom: zone.nom || zone,
        urgence: "Moyenne",
        score_total: 0,
        beneficiaires_prioritaires: 0,
        top5: [],
      })),
    })
    data.value = response.data
  } catch (err) {
    error.value = "Erreur lors de l'analyse de priorisation IA."
  } finally {
    loading.value = false
  }
}
</script>
