<template>
  <div class="self-stretch p-8 inline-flex flex-col justify-start items-start gap-8">
    <div class="self-stretch inline-flex justify-between items-end">
      <div class="size- inline-flex flex-col justify-start items-start gap-2">
        <div class="self-stretch flex flex-col justify-start items-start">
          <div class="justify-center text-yellow-800 text-4xl font-bold font-['Inter'] leading-9">Assistant Financier IA</div>
        </div>
        <div class="self-stretch flex flex-col justify-start items-start">
          <div class="justify-center text-gray-800 text-sm font-normal font-['Inter'] leading-5 tracking-tight">Analyse financière intelligente propulsée par IA.</div>
        </div>
      </div>
    </div>

    <div v-if="analysis" class="self-stretch bg-white rounded-xl shadow-[0px_4px_20px_0px_rgba(0,0,0,0.05)] p-6">
      <div class="mb-6">
        <div class="flex items-center gap-3 mb-4">
          <div class="w-4 h-4 rounded-full" :class="alertColorClass"></div>
          <div class="text-2xl font-bold" :class="alertTextClass">{{ analysis.ia_analysis?.niveau_alerte || 'Analyse en cours...' }}</div>
        </div>
        <div class="text-gray-700">{{ analysis.ia_analysis?.resume || 'Aucune analyse disponible' }}</div>
      </div>

      <div class="grid grid-cols-2 gap-6 mb-6">
        <div class="p-4 bg-gray-50 rounded-lg">
          <div class="text-sm font-semibold text-gray-600 mb-2">Observation</div>
          <div class="text-gray-800">{{ analysis.ia_analysis?.observation || '-' }}</div>
        </div>
        <div class="p-4 bg-gray-50 rounded-lg">
          <div class="text-sm font-semibold text-gray-600 mb-2">Prédiction</div>
          <div class="text-gray-800">{{ analysis.ia_analysis?.prediction || '-' }}</div>
        </div>
      </div>

      <div class="p-4 bg-yellow-50 rounded-lg border-l-4 border-yellow-500 mb-6">
        <div class="text-sm font-semibold text-yellow-800 mb-2">Recommandation</div>
        <div class="text-yellow-900">{{ analysis.ia_analysis?.recommandation || 'Aucune recommandation disponible' }}</div>
      </div>

      <div class="p-4 bg-blue-50 rounded-lg border-l-4 border-blue-500">
        <div class="text-sm font-semibold text-blue-800 mb-2">Justification</div>
        <div class="text-blue-900">{{ analysis.ia_analysis?.justification || 'Aucune justification disponible' }}</div>
      </div>
    </div>

    <div v-else class="self-stretch bg-white rounded-xl shadow-[0px_4px_20px_0px_rgba(0,0,0,0.05)] p-12 text-center">
      <div class="text-gray-500">Sélectionnez une campagne pour générer l'analyse IA</div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useFinanceStore } from '@/modules/finance/stores/financeStore.js'

const store = useFinanceStore()
const analysis = ref(null)

const alertColorClass = computed(() => {
  const level = analysis.value?.ia_analysis?.niveau_alerte || 'green'
  const colors = {
    green: 'bg-green-500',
    yellow: 'bg-yellow-500',
    orange: 'bg-orange-500',
    red: 'bg-red-500'
  }
  return colors[level] || colors.green
})

const alertTextClass = computed(() => {
  const level = analysis.value?.ia_analysis?.niveau_alerte || 'green'
  const colors = {
    green: 'text-green-600',
    yellow: 'text-yellow-600',
    orange: 'text-orange-600',
    red: 'text-red-600'
  }
  return colors[level] || colors.green
})
</script>