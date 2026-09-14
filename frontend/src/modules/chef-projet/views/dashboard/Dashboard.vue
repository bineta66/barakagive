<template>
  <div class="p-6 space-y-6 bg-white min-h-screen">
    <!-- Titre -->
    <div class=" pb-4">
      <h1 class="text-4xl font-bold text-or">Tableau de bord</h1>
      <p class="text-xs text-gray-500 mt-1">
        Vue d'ensemble de l'activitÃ© humanitaire.
      </p>
    </div>

    <!-- Cartes statistiques -->
    <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
      <div class="bg-white border border-slate-200/60 shadow rounded-xl p-4 flex justify-between">
        <div>
          <p class="text-xs font-bold uppercase text-slate-900">Projets actifs</p>
          <h3 class="text-xl font-bold text-or mt-2">8</h3>
        </div>
        <FolderKanban class="text-bleu-nuit" :size="28" />
      </div>

      <div class="bg-white border border-slate-200/60 shadow rounded-xl p-4 flex justify-between">
        <div>
          <p class="text-xs font-bold uppercase text-slate-900">Campagnes en cours</p>
          <h3 class="text-xl font-bold text-or mt-2">14</h3>
        </div>
        <ClipboardList class="text-bleu-nuit" :size="28" />
      </div>

      <div class="bg-white border border-slate-200/60 shadow rounded-xl p-4 flex justify-between">
        <div>
          <p class="text-xs font-bold uppercase text-slate-900">BÃ©nÃ©ficiaires</p>
          <h3 class="text-xl font-bold text-or mt-2">2 800</h3>
        </div>
        <Users class="text-bleu-nuit" :size="28" />
      </div>

      <div class="bg-white border border-slate-200/60 shadow rounded-xl p-4 flex justify-between">
        <div>
          <p class="text-xs font-bold uppercase text-slate-900">Budget allouÃ©</p>
          <h3 class="text-xl font-bold text-or mt-2">73 800 000 FCFA</h3>
        </div>
        <Wallet class="text-bleu-nuit" :size="28" />
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
import { FolderKanban, ClipboardList, Users, Wallet } from "lucide-vue-next"
import EvolutionChart from "@/components/ui/EvolutionChart.vue"
import ActiviteRecent from "@/components/ui/ActiviteRecent.vue"
</script>

