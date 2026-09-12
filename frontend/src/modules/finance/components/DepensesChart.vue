<template>
  <div class="bg-white border border-slate-200/60 rounded-xl p-6">
    <div class="flex justify-between items-center mb-4">
      <h3 class="text-sm font-bold uppercase text-slate-900">Répartition des dépenses</h3>
      <span class="text-xs text-slate-500">{{ formatMontant(totalDepenses) }} FCFA total</span>
    </div>

    <div class="space-y-3">
      <div
        v-for="item in depenses"
        :key="item.categorie"
        class="flex items-center gap-3"
      >
        <div class="w-4 h-4 rounded" :style="{ backgroundColor: item.couleur }"></div>
        <span class="text-sm font-medium text-slate-700 w-28">{{ item.categorie }}</span>
        <div class="flex-1 h-8 bg-slate-100 rounded relative overflow-hidden">
          <div
            class="h-full rounded transition-all flex items-center justify-end px-2"
            :style="{
              width: `${(item.montant / totalDepenses) * 100}%`,
              backgroundColor: item.couleur,
            }"
          >
            <span class="text-xs font-semibold text-white">{{ formatMontant(item.montant) }} FCFA</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from "vue"
import { useFinanceStore } from "@/modules/finance/stores/financeStore.js"

const store = useFinanceStore()

const depenses = computed(() => store.depensesParCategorie)
const formatMontant = store.formatMontant

const totalDepenses = computed(() => {
  return depenses.value.reduce((sum, d) => sum + d.montant, 0)
})
</script>
