<template>
  <div class="bg-white border border-slate-200/60 rounded-xl p-6 shadow-xs-sm">
    <div class="flex items-center justify-between mb-4">
      <div>
        <h2 class="text-base font-bold text-slate-900">Analyse budgétaire IA</h2>
        <p class="text-xs text-gray-500 mt-1">
          Synthèse générée à partir des dépenses réelles du projet.
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
          <p class="text-xs text-gray-500">Alerte</p>
          <p class="text-sm font-semibold" :class="alerteClass">{{ data.alerte }}</p>
        </div>
        <div class="p-3 rounded-lg border border-slate-100">
          <p class="text-xs text-gray-500">Catégorie principale</p>
          <p class="text-sm font-semibold text-slate-900">{{ data.categorie_plus_depensiere }}</p>
        </div>
        <div class="p-3 rounded-lg border border-slate-100">
          <p class="text-xs text-gray-500">Zone la plus dépensière</p>
          <p class="text-sm font-semibold text-slate-900">{{ data.zone_plus_depensiere }}</p>
        </div>
      </div>

      <p class="text-xs text-gray-500">
        Généré le {{ generatedAt }}
      </p>
    </div>

    <div v-else class="text-xs text-gray-500">
      Appuyez sur Évaluer pour générer l’analyse budgétaire IA.
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from "vue"
import api from "@/services/api.js"

const props = defineProps({
  projetId: {
    type: [String, Number],
    default: null,
  },
})

const loading = ref(false)
const error = ref(null)
const data = ref(null)

const alerteClass = computed(() => {
  const a = data.value?.alerte || ""
  if (a === "Vert") return "text-green-700"
  if (a === "Jaune") return "text-yellow-700"
  if (a === "Orange") return "text-orange-700"
  if (a === "Rouge") return "text-red-700"
  return "text-slate-900"
})

const generatedAt = computed(() => {
  if (!data.value?.generated_at) return ""
  return new Date(data.value.generated_at).toLocaleString("fr-FR")
})

const evaluate = async () => {
  if (!props.projetId) return
  loading.value = true
  error.value = null
  data.value = null
  try {
    const response = await api.post(`/api/ia/budget`, {
      projet: String(props.projetId),
      budget_total: 0,
      dons_recus: 0,
      depenses_totales: 0,
      solde: 0,
      taux_execution: 0,
      depenses: [],
    })
    data.value = response.data
  } catch (err) {
    error.value = "Erreur lors de l'analyse budgétaire IA."
  } finally {
    loading.value = false
  }
}
</script>
