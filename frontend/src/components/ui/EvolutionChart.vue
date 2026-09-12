<template>
  <div class="self-stretch flex flex-col justify-start items-start gap-4">
    <!-- En-tête -->
    <div class="self-stretch inline-flex justify-between items-center">
      <div class="inline-flex flex-col justify-start items-start gap-0.5">
        <div class="text-slate-700 text-sm font-bold uppercase leading-5 tracking-wide">
          ÉVOLUTION DES PROJETS ET BÉNÉFICIAIRES
        </div>
        <div class="text-gray-500 text-xs font-normal leading-4">
          Progression mensuelle cumulée sur les 6 derniers mois (2025)
        </div>
      </div>

      <!-- Légende -->
      <div class="inline-flex justify-start items-center gap-6">
        <div class="flex items-center gap-2">
          <div class="w-3 h-3 bg-sky-900 rounded"></div>
          <span class="text-slate-600 text-xs">Projets</span>
        </div>
        <div class="flex items-center gap-2">
          <div class="w-3 h-3 bg-yellow-800 rounded"></div>
          <span class="text-slate-600 text-xs">Bénéficiaires (x100)</span>
        </div>
      </div>
    </div>

    <!-- Graphique -->
    <div class="self-stretch h-64 relative">
      <!-- Grille horizontale -->
      <div
        v-for="i in 5"
        :key="`grid-${i}`"
        class="absolute left-0 right-0 border-t border-slate-100"
        :style="{ top: `${i * 20}%` }"
      ></div>

      <!-- Barres -->
      <div class="absolute bottom-0 left-0 right-0 h-full flex items-end justify-between pl-2">
        <div
          v-for="item in dataMensuelle"
          :key="item.mois"
          class="flex items-end gap-1 h-full justify-center flex-1"
        >
          <!-- Barre Projet -->
          <div
            class="w-4 bg-sky-900 rounded-t transition-all"
            :style="{ height: `${item.projets}%` }"
            :title="`${item.mois} - Projets: ${item.projets}%`"
          ></div>
          <!-- Barre Bénéficiaires -->
          <div
            class="w-4 bg-yellow-800 opacity-90 rounded-t transition-all"
            :style="{ height: `${item.beneficiaires}%` }"
            :title="`${item.mois} - Bénéficiaires: ${item.beneficiaires}%`"
          ></div>
        </div>
      </div>
    </div>

    <!-- Labels mensuels -->
    <div class="self-stretch pt-3 inline-flex justify-between items-start">
      <div
        v-for="item in dataMensuelle"
        :key="item.mois"
        class="flex-1 flex justify-center"
      >
        <div class="text-center">
          <div
            class="text-xs font-semibold"
            :class="item.mois === 'Juin' ? 'text-sky-700 font-bold' : 'text-gray-500'"
          >
            {{ item.mois }}
          </div>
          <span v-if="item.mois === 'Juin'" class="text-xs text-gray-500">(en cours)</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from "vue"

const dataMensuelle = ref([
  { mois: "Janvier", projets: 25, beneficiaires: 35 },
  { mois: "Février", projets: 35, beneficiaires: 45 },
  { mois: "Mars", projets: 30, beneficiaires: 50 },
  { mois: "Avril", projets: 45, beneficiaires: 55 },
  { mois: "Mai", projets: 40, beneficiaires: 60 },
  { mois: "Juin", projets: 50, beneficiaires: 65 },
])
</script>
