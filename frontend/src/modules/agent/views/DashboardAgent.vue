<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-2xl font-bold text-or">
          Tableau de bord Agent de terrain
        </h1>
        <p class="text-sm text-slate-500 mt-1">
          Suivi de vos campagnes et collectes sur le terrain
        </p>
      </div>
    </div>

    <!-- KPI Cards -->
    <div class="grid grid-cols-1 md:grid-cols-4 gap-5">
      <KpiCard
        titre="Campagnes totales"
        :valeur="statistiques.campagnesTotales"
        :icone="FolderKanban"
        couleur="sky"
      />
      <KpiCard
        titre="En cours"
        :valeur="statistiques.campagnesEnCours"
        :icone="Activity"
        couleur="emerald"
      />
      <KpiCard
        titre="Collecte totale"
        :valeur="formatMontant(statistiques.collecteTotale) + ' FCFA'"
        :icone="PiggyBank"
        couleur="amber"
      />
      <KpiCard
        titre="Taux de rÃ©alisation"
        :valeur="statistiques.tauxRealisation + '%'"
        :icone="TrendingUp"
        couleur="purple"
      />
    </div>

    <!-- Campaigns Status -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-5">
      <StatCard
        titre="Campagnes planifiÃ©es"
        :valeur="statistiques.campagnesPlanifiees"
        :icone="Calendar"
        couleur="sky"
      />
      <StatCard
        titre="Campagnes terminÃ©es"
        :valeur="statistiques.campagnesTerminees"
        :icone="CheckCircle"
        couleur="emerald"
      />
      <StatCard
        titre="Collectes terrain"
        :valeur="statistiques.collectesTerrain"
        :icone="MapPin"
        couleur="amber"
      />
    </div>

    <!-- Sync Status -->
    <div class="grid grid-cols-1 md:grid-cols-2 gap-5">
      <StatCard
        titre="Ã‰lÃ©ments synchronisÃ©s"
        :valeur="statistiques.elementsSynchronises"
        :icone="Cloud"
        couleur="emerald"
      />
      <StatCard
        titre="En attente de sync"
        :valeur="statistiques.elementsEnAttente"
        :icone="Clock"
        couleur="orange"
      />
    </div>

    <!-- Recent Campaigns -->
    <div class="bg-white border border-slate-200/60 rounded-xl">
      <div class="px-5 py-4 ">
        <h2 class="text-lg font-semibold text-slate-900">
          Mes campagnes rÃ©centes
        </h2>
      </div>
      <div class="overflow-x-auto">
        <table class="w-full">
          <thead class="bg-slate-50">
            <tr>
              <th class="text-left px-4 py-3 text-xs font-medium text-bleu-nuit uppercase tracking-wider">
                Campagne
              </th>
              <th class="text-left px-4 py-3 text-xs font-medium text-bleu-nuit uppercase tracking-wider">
                ONG
              </th>
              <th class="text-left px-4 py-3 text-xs font-medium text-bleu-nuit uppercase tracking-wider">
                Zone
              </th>
              <th class="text-left px-4 py-3 text-xs font-medium text-bleu-nuit uppercase tracking-wider">
                Statut
              </th>
              <th class="text-left px-4 py-3 text-xs font-medium text-bleu-nuit uppercase tracking-wider">
                Collecte
              </th>
              <th class="text-left px-4 py-3 text-xs font-medium text-bleu-nuit uppercase tracking-wider">
                Objectif
              </th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-100">
            <tr v-for="campagne in campagnes" :key="campagne.id">
              <td class="px-4 py-3 text-sm font-medium text-slate-900">
                {{ campagne.nom }}
              </td>
              <td class="px-4 py-3 text-sm text-slate-600">{{ campagne.ONG }}</td>
              <td class="px-4 py-3 text-sm text-slate-600">{{ campagne.zone }}</td>
              <td class="px-4 py-3">
                <span
                  class="inline-block px-2 py-1 text-xs font-medium rounded-full"
                  :class="
                    campagne.statut === 'En cours'
                      ? 'text-sky-700 bg-sky-50'
                      : campagne.statut === 'TerminÃ©'
                      ? 'text-emerald-700 bg-emerald-50'
                      : campagne.statut === 'PlanifiÃ©'
                      ? 'text-purple-700 bg-purple-50'
                      : 'text-slate-700 bg-slate-100'
                  "
                >
                  {{ campagne.statut }}
                </span>
              </td>
              <td class="px-4 py-3 text-sm text-slate-600">
                {{ formatMontant(campagne.collecte) }} FCFA
              </td>
              <td class="px-4 py-3 text-sm text-slate-600">
                {{ formatMontant(campagne.objectif) }} FCFA
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useAgentStore } from "@/modules/agent/stores/agentStore.js"
import {
  FolderKanban,
  Activity,
  PiggyBank,
  TrendingUp,
  Calendar,
  CheckCircle,
  MapPin,
  Cloud,
  Clock,
} from "lucide-vue-next"
import KpiCard from "@/components/ui/KpiCard.vue"
import StatCard from "@/components/ui/StatCard.vue"

const store = useAgentStore()
const { campagnes, statistiques, formatMontant } = store
</script>





