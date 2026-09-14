<template>
  <div class="bg-white border border-slate-200/60 rounded-xl overflow-hidden">
    <div class="flex justify-between items-center px-6 py-4 ">
      <h3 class="text-sm font-bold uppercase text-slate-900">Mes projets assignÃ©s</h3>
      <span class="text-xs text-slate-500">{{ projets.length }} projet(s)</span>
    </div>

    <table class="w-full">
      <thead class="bg-slate-50 text-xs uppercase text-bleu-nuit">
        <tr>
          <th class="text-left px-4 py-3">Projet</th>
          <th class="text-left px-4 py-3">Chef de projet</th>
          <th class="text-right px-4 py-3">Budget allouÃ©</th>
          <th class="text-center px-4 py-3">Statut</th>
        </tr>
      </thead>
      <tbody>
        <tr
          v-for="projet in projets"
          :key="projet.id"
          class="border-t hover:bg-slate-50"
        >
          <td class="px-4 py-3">
            <h4 class="font-semibold text-sm text-slate-800">{{ projet.nom }}</h4>
            <p class="text-xs text-gray-500">{{ projet.code }}</p>
          </td>
          <td class="px-4 py-3 text-sm text-slate-700">{{ projet.chefProjet }}</td>
          <td class="px-4 py-3 text-right text-sm font-semibold text-slate-900">{{ formatMontant(projet.budget) }} FCFA</td>
          <td class="px-4 py-3 text-center">
             <StatusBadge :statut="projet.statut">{{ projet.statut }}</StatusBadge>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script setup>
import StatusBadge from "@/components/ui/StatusBadge.vue"
import { useFinanceStore } from "@/modules/finance/stores/financeStore.js"

const store = useFinanceStore()

const { projetsAssignes: projets, formatMontant } = store
</script>

