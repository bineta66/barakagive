<template>
  <div class="p-6 space-y-6 bg-white min-h-screen">
    <!-- Header -->
    <div class="flex justify-between items-center  pb-4">
      <div>
        <h1 class="text-4xl font-bold text-or">Dashboard</h1>
        <p class="text-xs text-gray-500 mt-1">
          Vue d'ensemble des projets, utilisateurs et finances.
        </p>
      </div>
      <BoutonPrimary>
        <Download :size="16" />
        Exporter rapport
      </BoutonPrimary>
    </div>

    <!-- KPI Cards -->
    <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
      <div class="bg-white border border-slate-200/60 shadow rounded-xl p-4 flex justify-between">
        <div>
          <p class="text-xs font-bold uppercase text-slate-900">Projets actifs</p>
          <h3 class="text-xl font-bold text-or mt-2">{{ statistiques.totalProjets }}</h3>
        </div>
        <FolderKanban class="text-bleu-nuit" :size="28" />
      </div>

      <div class="bg-white border border-slate-200/60 shadow rounded-xl p-4 flex justify-between">
        <div>
          <p class="text-xs font-bold uppercase text-slate-900">Utilisateurs</p>
          <h3 class="text-xl font-bold text-or mt-2">{{ statistiques.totalUtilisateurs }}</h3>
        </div>
        <Users class="text-bleu-nuit" :size="28" />
      </div>

      <div class="bg-white border border-slate-200/60 shadow rounded-xl p-4 flex justify-between">
        <div>
          <p class="text-xs font-bold uppercase text-slate-900">Budget allouÃ©</p>
          <h3 class="text-xl font-bold text-or mt-2">{{ formatMontant(statistiques.budgetTotal) }} FCFA</h3>
        </div>
        <Wallet class="text-bleu-nuit" :size="28" />
      </div>

      <div class="bg-white border border-slate-200/60 shadow rounded-xl p-4 flex justify-between">
        <div>
          <p class="text-xs font-bold uppercase text-slate-900">Taux d'exÃ©cution</p>
          <h3 class="text-xl font-bold text-or mt-2">{{ statistiques.tauxExecution }}%</h3>
        </div>
        <Activity class="text-bleu-nuit" :size="28" />
      </div>
    </div>

    <!-- Graphique + ActivitÃ© rÃ©cente -->
    <div class="flex gap-6">
      <div class="flex-[2] min-w-0">
        <div class="bg-white border border-slate-200/60 rounded-xl p-6 h-full">
          <EvolutionChart />
        </div>
      </div>

      <div class="flex-[1] min-w-0">
        <div class="bg-white border border-slate-200/60 rounded-xl h-full">
          <ActiviteRecent />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from "vue"
import {
  Download,
  FolderKanban,
  Users,
  Wallet,
  Activity,
} from "lucide-vue-next"
import { useGerantStore } from "@/modules/gerant/stores/gerantStore.js"
import BoutonPrimary from "@/components/ui/BoutonPrimary.vue"
import EvolutionChart from "@/components/ui/EvolutionChart.vue"
import ActiviteRecent from "@/components/ui/ActiviteRecent.vue"

const store = useGerantStore()
const { formatMontant } = store

const statistiques = computed(() => store.statistiques)
</script>

