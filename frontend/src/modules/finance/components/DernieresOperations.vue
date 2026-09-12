<template>
  <div class="bg-white border border-slate-200/60 rounded-xl overflow-hidden">
    <div class="flex justify-between items-center px-6 py-4 border-b border-slate-200">
      <h3 class="text-sm font-bold uppercase text-slate-900">Dernières opérations</h3>
    </div>

    <table class="w-full">
      <thead class="bg-slate-50 text-xs uppercase text-sky-900">
        <tr>
          <th class="text-left px-4 py-3">Date</th>
          <th class="text-left px-4 py-3">Libellé</th>
          <th class="text-right px-4 py-3">Montant</th>
        </tr>
      </thead>
      <tbody>
        <tr
          v-for="operation in operations"
          :key="operation.id"
          class="border-t hover:bg-slate-50"
        >
          <td class="px-4 py-3 text-sm text-slate-600">{{ operation.date }}</td>
          <td class="px-4 py-3 text-sm text-slate-700">{{ operation.libelle }}</td>
          <td class="px-4 py-3 text-right">
            <span
              class="text-sm font-semibold"
              :class="{
                'text-red-600': operation.type === 'depense',
                'text-emerald-700': operation.type === 'don',
              }"
            >
              {{ operation.type === 'depense' ? '-' : '+' }}{{ formatMontant(operation.montant) }} FCFA
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

const { dernieresOperations: operations, formatMontant } = store
</script>
