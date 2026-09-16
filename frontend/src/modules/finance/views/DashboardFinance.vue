<template>
  <div class="p-6 space-y-6 bg-white min-h-screen">
    <!-- En-tête -->
    <div class="flex justify-between items-center  pb-4">
      <div>
        <h1 class="text-4xl font-bold text-or">Tableau de bord Finance</h1>
        <p class="text-xs text-gray-500 mt-1">
          Voici un aperçu financier de vos projets et campagnes sous mandat direct.
        </p>
      </div>
      <div class="px-4 py-2 bg-bleu-nuit flex items-center gap-1 rounded-lg">
        <div class="w-3 h-3 bg-white"></div>
        <span class="text-white text-sm font-semibold">Exporter arrêté</span>
      </div>
    </div>

    <!-- KPI Cards -->
    <DashboardKpiCards />

    <!-- Chart Section -->
    <FinanceEvolutionChart />
  </div>
</template>

<script setup>
import DashboardKpiCards from "@/modules/finance/components/DashboardKpiCards.vue"
import FinanceEvolutionChart from "@/modules/finance/components/FinanceEvolutionChart.vue"
</script>


