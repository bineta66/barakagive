<template>
  <div class="self-stretch p-8 inline-flex flex-col justify-start items-start gap-8">
    <div class="self-stretch inline-flex justify-between items-end">
      <div class="size- inline-flex flex-col justify-start items-start gap-2">
        <div class="self-stretch flex flex-col justify-start items-start">
          <div class="justify-center text-yellow-800 text-4xl font-bold font-['Inter'] leading-9">Rapports Financiers</div>
        </div>
        <div class="self-stretch flex flex-col justify-start items-start">
          <div class="justify-center text-gray-800 text-sm font-normal font-['Inter'] leading-5 tracking-tight">Génération de rapports financiers exportables.</div>
        </div>
      </div>
    </div>

    <div class="self-stretch bg-white rounded-xl shadow-[0px_4px_20px_0px_rgba(0,0,0,0.05)] p-6">
      <div class="flex gap-4 mb-6">
        <button @click="generatePDF" class="px-6 py-3 bg-red-600 text-white rounded-lg flex items-center gap-2">
          <span>Générer PDF</span>
        </button>
        <button @click="generateExcel" class="px-6 py-3 bg-green-600 text-white rounded-lg flex items-center gap-2">
          <span>Générer Excel</span>
        </button>
      </div>

      <div class="space-y-4">
        <div class="p-4 bg-gray-50 rounded-lg">
          <div class="text-sm font-semibold text-gray-600 mb-2">Budget initial</div>
          <div class="text-2xl font-bold text-gray-800">{{ formatMontant(store.dashboard?.budget_total) }} FCFA</div>
        </div>
        <div class="p-4 bg-gray-50 rounded-lg">
          <div class="text-sm font-semibold text-gray-600 mb-2">Dons reçus</div>
          <div class="text-2xl font-bold text-emerald-600">{{ formatMontant(store.dashboard?.dons_reçus) }} FCFA</div>
        </div>
        <div class="p-4 bg-gray-50 rounded-lg">
          <div class="text-sm font-semibold text-gray-600 mb-2">Dépenses</div>
          <div class="text-2xl font-bold text-red-600">{{ formatMontant(store.dashboard?.depenses_totales) }} FCFA</div>
        </div>
        <div class="p-4 bg-gray-50 rounded-lg">
          <div class="text-sm font-semibold text-gray-600 mb-2">Solde</div>
          <div class="text-2xl font-bold text-gray-800">{{ formatMontant(store.dashboard?.solde_disponible) }} FCFA</div>
        </div>
        <div class="p-4 bg-gray-50 rounded-lg">
          <div class="text-sm font-semibold text-gray-600 mb-2">Taux d'exécution</div>
          <div class="text-2xl font-bold text-gray-800">{{ store.dashboard?.taux_execution }}%</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { useFinanceStore } from '@/modules/finance/stores/financeStore.js'

const store = useFinanceStore()

const formatMontant = (value) => {
  return Number(value || 0).toLocaleString('fr-FR')
}

const generatePDF = () => {
  alert('Génération PDF - À implémenter avec une librairie comme jsPDF')
}

const generateExcel = () => {
  alert('Génération Excel - À implémenter avec une librairie comme xlsx')
}

onMounted(() => {
  store.fetchDashboard()
})
</script>