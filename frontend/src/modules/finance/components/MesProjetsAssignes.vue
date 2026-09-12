<template>
  <div class="bg-white border border-slate-200/60 rounded-xl overflow-hidden">
    <div class="flex justify-between items-center px-6 py-4 border-b border-slate-200">
      <h3 class="text-sm font-bold uppercase text-slate-900">Mes projets assignés</h3>
      <span class="text-xs text-slate-500">{{ projets.length }} projet(s)</span>
    </div>

    <table class="w-full">
      <thead class="bg-slate-50 text-xs uppercase text-sky-900">
        <tr>
          <th class="text-left px-4 py-3">Projet</th>
          <th class="text-left px-4 py-3">Chef de projet</th>
          <th class="text-right px-4 py-3">Budget alloué</th>
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
            <span
              class="px-2 py-1 rounded text-xs font-semibold"
              :class="{
                'bg-emerald-100 text-emerald-700': projet.statut === 'En cours',
                'bg-sky-100 text-sky-700': projet.statut === 'Budgétisé',
                'bg-amber-100 text-amber-700': projet.statut === 'À budgétiser',
              }"
            >
              {{ projet.statut }}
            </span>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script setup>
import { useFinanceStore } from "@/modules/finance/stores/financeStore.js"

const store = useFinanceStore()

const { projetsAssignes: projets, formatMontant } = store
</script>
