<template>
  <div class="p-6 space-y-6 bg-white min-h-screen">
    <!-- En-tête -->
    <div class="flex justify-between items-center  pb-4">
      <div>
        <h1 class="text-4xl font-bold text-or">Rapports financiers</h1>
        <p class="text-xs text-gray-500 mt-1">
          Analyse détaillée des performances budgétaires et financières
        </p>
      </div>
    </div>

    <!-- Cartes KPI -->
    <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
      <div class="bg-white border border-slate-200/60 shadow-xs rounded-xl p-4 flex justify-between">
        <div>
          <p class="text-xs font-bold uppercase text-slate-900">Budget total</p>
          <h3 class="text-xl font-bold text-or mt-2">{{ formatMontant(stats.budgetTotal) }} FCFA</h3>
        </div>
        <PiggyBank class="text-bleu-nuit" :size="28" />
      </div>

      <div class="bg-white border border-slate-200/60 shadow-xs rounded-xl p-4 flex justify-between">
        <div>
          <p class="text-xs font-bold uppercase text-slate-900">Dépenses réalisées</p>
          <h3 class="text-xl font-bold text-or mt-2">{{ formatMontant(stats.depensesRealisees) }} FCFA</h3>
        </div>
        <Receipt class="text-bleu-nuit" :size="28" />
      </div>

      <div class="bg-white border border-slate-200/60 shadow-xs rounded-xl p-4 flex justify-between">
        <div>
          <p class="text-xs font-bold uppercase text-slate-900">Solde disponible</p>
          <h3 class="text-xl font-bold text-or mt-2">{{ formatMontant(stats.soldeDisponible) }} FCFA</h3>
        </div>
        <Banknote class="text-bleu-nuit" :size="28" />
      </div>

      <div class="bg-white border border-slate-200/60 shadow-xs rounded-xl p-4 flex justify-between">
        <div>
          <p class="text-xs font-bold uppercase text-slate-900">Taux d'exécution</p>
          <h3 class="text-xl font-bold text-or mt-2">{{ stats.tauxExecution }}%</h3>
        </div>
        <TrendingUp class="text-bleu-nuit" :size="28" />
      </div>
    </div>

    <!-- Graphiques -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-4">
      <!-- Répartition par projet -->
      <div class="bg-white border border-slate-200/60 rounded-xl p-5">
        <h2 class="text-lg font-semibold text-slate-900 mb-4">Répartition budgétaire par projet</h2>
        <div class="space-y-3">
          <div
            v-for="budget in store.budgets"
            :key="budget.id"
            class="flex items-center gap-3"
          >
            <div class="w-24 text-xs text-slate-600">{{ budget.projet }}</div>
            <div class="flex-1 bg-slate-100 rounded-full h-4 overflow-hidden">
              <div
                class="h-full bg-or rounded-full transition-all"
                :style="{ width: budgetPourcentage(budget) + '%' }"
              ></div>
            </div>
            <div class="w-28 text-right text-sm font-semibold text-slate-900">
              {{ formatMontant(budget.consomme) }} / {{ formatMontant(budget.budgetTotal) }}
            </div>
          </div>
        </div>
      </div>

      <!-- Dernières opérations -->
      <div class="bg-white border border-slate-200/60 rounded-xl p-5">
        <h2 class="text-lg font-semibold text-slate-900 mb-4">Dernières opérations</h2>
        <div class="space-y-3">
          <div
            v-for="operation in dernieresOperations"
            :key="operation.id"
            class="flex justify-between items-center py-2 border-t border-slate-100 first:border-0"
          >
            <div>
              <p class="text-sm font-medium text-slate-900">{{ operation.libelle }}</p>
              <p class="text-xs text-slate-500">{{ operation.date }}</p>
            </div>
            <div class="text-right">
              <p
                class="text-sm font-semibold"
                :class="operation.type === 'don' ? 'text-bleu-nuit' : 'text-red-700'"
              >
                {{ formatMontant(operation.montant) }} FCFA
              </p>
              <p class="text-xs text-slate-500">
                {{ operation.type === 'don' ? 'Entrée' : 'Sortie' }}
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Tableau des projets -->
    <div class="bg-white border border-slate-200/60 rounded-xl overflow-hidden">
      <div class="px-5 py-4 ">
        <h2 class="text-lg font-semibold text-slate-900">Synthèse par projet</h2>
      </div>
      <div class="overflow-x-auto">
        <table class="w-full">
          <thead class="bg-slate-50">
            <tr>
              <th class="text-left px-4 py-3 text-xs font-medium text-bleu-nuit uppercase tracking-wider">
                Projet
              </th>
              <th class="text-right px-4 py-3 text-xs font-medium text-bleu-nuit uppercase tracking-wider">
                Budget
              </th>
              <th class="text-right px-4 py-3 text-xs font-medium text-bleu-nuit uppercase tracking-wider">
                Consommé
              </th>
              <th class="text-right px-4 py-3 text-xs font-medium text-bleu-nuit uppercase tracking-wider">
                Solde
              </th>
              <th class="text-left px-4 py-3 text-xs font-medium text-bleu-nuit uppercase tracking-wider">
                Statut
              </th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-100">
            <tr v-for="budget in store.budgets" :key="budget.id">
              <td class="px-4 py-3 text-sm font-medium text-slate-900">
                {{ budget.projet }}
              </td>
              <td class="px-4 py-3 text-right text-sm text-slate-600">
                {{ formatMontant(budget.budgetTotal) }} FCFA
              </td>
              <td class="px-4 py-3 text-right text-sm text-or font-semibold">
                {{ formatMontant(budget.consomme) }} FCFA
              </td>
              <td class="px-4 py-3 text-right text-sm text-bleu-nuit font-semibold">
                {{ formatMontant(budget.solde) }} FCFA
              </td>
              <td class="px-4 py-3">
                <StatusBadge :statut="budget.statut">{{ budget.statut }}</StatusBadge>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from "vue"
import {
  PiggyBank,
  Receipt,
  Banknote,
  TrendingUp,
} from "lucide-vue-next"
import { useFinanceStore } from "@/modules/finance/stores/financeStore.js"
import FinancialOrbital from "@/components/ia/FinancialOrbital.vue"

const store = useFinanceStore()
const { formatMontant } = store

const stats = computed(() => store.statistiques)
const dernieresOperations = computed(() => store.dernieresOperations)

const budgetPourcentage = (budget) => {
  if (budget.budgetTotal > 0) {
    return Math.round((budget.consomme / budget.budgetTotal) * 100)
  }
  return 0
}

const badgeClass = (statut) => {
  switch (statut) {
    case "En cours":
      return "bg-bleu-nuit/10 text-bleu-nuit"
    case "Terminée":
      return "bg-or/10 text-bleu-nuit"
    case "Planifiée":
      return "bg-purple-100 text-purple-700"
    case "À budgétiser":
      return "bg-or/10 text-or"
    default:
      return "bg-gray-100 text-gray-600"
  }
}
</script>

<FinancialOrbital />


