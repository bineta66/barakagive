<template>
  <div class="bg-white border border-slate-200/60 rounded-xl p-6">
    <!-- En-tête -->
    <div class="flex justify-between items-center mb-4">
      <div>
        <h3 class="text-sm font-bold uppercase text-slate-900">Mes projets assignés</h3>
        <p class="text-xs text-gray-500 mt-1">Budget alloué par projet</p>
      </div>
      <span class="text-xs text-slate-500">{{ projets.length }} projet(s)</span>
    </div>

    <!-- Graphique -->
    <div class="space-y-4">
      <div
        v-for="projet in projets"
        :key="projet.id"
        class="flex items-center gap-3"
      >
        <!-- Nom + chef -->
        <div class="w-48 flex-shrink-0">
          <p class="text-sm font-semibold text-slate-800">{{ projet.nom }}</p>
          <p class="text-xs text-gray-500">{{ projet.chefProjet }}</p>
        </div>

        <!-- Barre -->
        <div class="flex-1 relative h-8">
          <div
            class="h-full rounded transition-all flex items-center justify-end px-2"
            :style="{
              width: `${(projet.budget / budgetMax) * 100}%`,
              backgroundColor: couleurStatut(projet.statut),
            }"
          >
            <span class="text-xs font-semibold text-white">{{ formatMontant(projet.budget) }} FCFA</span>
          </div>
        </div>

        <!-- Statut -->
        <div class="w-32 flex-shrink-0 text-center">
          <StatusBadge :statut="projet.statut">
            {{ projet.statut }}
          </StatusBadge>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from "vue"
import { useFinanceStore } from "@/modules/finance/stores/financeStore.js"
import StatusBadge from "@/components/ui/StatusBadge.vue"

const store = useFinanceStore()

const projets = computed(() => store.projetsAssignes)
const formatMontant = store.formatMontant

const budgetMax = computed(() => {
  return Math.max(...projets.value.map(p => p.budget), 1)
})

const couleurStatut = (statut) => {
  switch (statut) {
    case "En cours":
      return "#F59E0B"
    case "Budgétisé":
      return "#10B981"
    case "À budgétiser":
      return "#6B7280"
    default:
      return "#9CA3AF"
  }
}

const badgeClass = (statut) => {
  switch (statut) {
    case "En cours":
      return "bg-bleu-nuit/10 text-bleu-nuit"
    case "Budgétisé":
      return "bg-or/10 text-bleu-nuit"
    case "À budgétiser":
      return "bg-or/10 text-or"
    default:
      return "bg-gray-100 text-gray-600"
  }
}
</script>


