<template>
  <div class="bg-white border border-slate-200/60 rounded-xl shadow-xs-[0px_1px_2px_0px_rgba(0,0,0,0.05)] overflow-hidden">
    <div class="p-6">
      <h3 class="text-lg font-bold text-gray-900">Bénéficiaires les plus urgents</h3>
      <p class="text-xs text-gray-500 mt-1">Top 5 de la zone sélectionnée</p>
    </div>
    <div class="p-6">
      <div v-if="beneficiaires.length === 0" class="text-sm text-gray-500">Aucun bénéficiaire urgent dans cette zone.</div>
      <div v-else class="space-y-3">
        <div
          v-for="beneficiaire in beneficiaires"
          :key="beneficiaire.id"
          class="flex items-center justify-between p-3 bg-gray-50 rounded-lg border border-gray-200"
        >
          <div>
            <p class="text-sm font-medium text-gray-900">{{ beneficiaire.prenom }} {{ beneficiaire.nom }}</p>
            <p class="text-xs text-gray-500">{{ beneficiaire.zone }}</p>
          </div>
          <div class="flex items-center gap-2">
            <span class="text-xs font-semibold text-gray-700">Score IA: {{ beneficiaire.scoreIA }}</span>
            <span
              class="px-2 py-1 rounded text-xs font-semibold"
              :class="beneficiaire.statut === 'Critique' ? 'bg-red-100 text-red-700' : 'bg-orange-100 text-orange-700'"
            >
              {{ beneficiaire.statut }}
            </span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  beneficiaires: {
    type: Array,
    required: true,
  },
})
</script>


