<template>
  <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
    <!-- BUDGET TOTAL ALLOUÉ -->
    <div class="bg-white border border-slate-200/60 rounded-xl p-4 flex justify-between">
      <div>
        <p class="text-xs font-bold uppercase text-slate-900">Budget total alloué</p>
        <h3 class="text-xl font-bold text-yellow-800 mt-2">{{ formatMontant(statistiques.budgetTotal) }} FCFA</h3>
      </div>
      <PiggyBank class="text-slate-400" :size="28" />
    </div>

    <!-- DÉPENSES RÉALISÉES -->
    <div class="bg-white border border-slate-200/60 rounded-xl p-4 flex justify-between">
      <div>
        <p class="text-xs font-bold uppercase text-slate-900">Dépenses réalisées</p>
        <h3 class="text-xl font-bold text-slate-900 mt-2">{{ formatMontant(statistiques.depensesRealisees) }} FCFA</h3>
      </div>
      <Receipt class="text-slate-400" :size="28" />
    </div>

    <!-- SOLDE RESTANT -->
    <div class="bg-white border border-slate-200/60 rounded-xl p-4 flex justify-between">
      <div>
        <p class="text-xs font-bold uppercase text-slate-900">Solde disponible</p>
        <h3 class="text-xl font-bold text-green-700 mt-2">{{ formatMontant(statistiques.soldeDisponible) }} FCFA</h3>
      </div>
      <Banknote class="text-slate-400" :size="28" />
    </div>

    <!-- CAMPAGNES FINANCÉES -->
    <div class="bg-white border border-slate-200/60 rounded-xl p-4 flex justify-between">
      <div>
        <p class="text-xs font-bold uppercase text-slate-900">Campagnes financées</p>
        <h3 class="text-xl font-bold text-purple-700 mt-2">{{ statistiques.campagnesFinancées }} actives</h3>
      </div>
      <Activity class="text-slate-400" :size="28" />
    </div>
  </div>
</template>

<script setup>
import { PiggyBank, Receipt, Banknote, Activity } from "lucide-vue-next"
import { useFinanceStore } from "@/modules/finance/stores/financeStore.js"

const store = useFinanceStore()

const { statistiques, formatMontant } = store
</script>
