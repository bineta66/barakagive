<template>
  <div class="p-6 space-y-6 bg-white min-h-screen">
    <!-- En-tÃªte -->
    <div class="flex justify-between items-center  pb-4">
      <div>
        <h1 class="text-4xl font-bold text-or">Mon ONG</h1>
        <p class="text-xs text-gray-500 mt-1">
          Gestion des informations, bailleurs et partenaires de votre organisation.
        </p>
      </div>
    </div>

    <!-- Cartes KPI -->
    <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
      <div class="bg-white border border-slate-200/60 shadow rounded-xl p-4 flex justify-between">
        <div>
          <p class="text-xs font-bold uppercase text-slate-900">Bailleurs</p>
          <h3 class="text-xl font-bold text-or mt-2">{{ statistiques.bailleursCount }}</h3>
        </div>
        <PiggyBank class="text-bleu-nuit" :size="28" />
      </div>

      <div class="bg-white border border-slate-200/60 shadow rounded-xl p-4 flex justify-between">
        <div>
          <p class="text-xs font-bold uppercase text-slate-900">Partenaires</p>
          <h3 class="text-xl font-bold text-or mt-2">{{ statistiques.partenairesCount }}</h3>
        </div>
        <Users class="text-bleu-nuit" :size="28" />
      </div>

      <div class="bg-white border border-slate-200/60 shadow rounded-xl p-4 flex justify-between">
        <div>
          <p class="text-xs font-bold uppercase text-slate-900">Budget total</p>
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

    <!-- Bailleurs Table -->
    <div class="bg-white border border-slate-200/60 rounded-xl overflow-hidden">
      <div class="px-5 py-4 ">
        <h2 class="text-lg font-semibold text-slate-900">Bailleurs</h2>
      </div>
      <div class="overflow-x-auto">
        <table class="w-full">
          <thead class="bg-slate-50">
            <tr>
              <th class="text-left px-4 py-3 text-xs font-medium text-bleu-nuit uppercase tracking-wider">
                Organisation
              </th>
              <th class="text-left px-4 py-3 text-xs font-medium text-bleu-nuit uppercase tracking-wider">
                Contact
              </th>
              <th class="text-left px-4 py-3 text-xs font-medium text-bleu-nuit uppercase tracking-wider">
                Type
              </th>
              <th class="text-right px-4 py-3 text-xs font-medium text-bleu-nuit uppercase tracking-wider">
                Projets
              </th>
              <th class="text-right px-4 py-3 text-xs font-medium text-bleu-nuit uppercase tracking-wider">
                Financement
              </th>
              <th class="text-left px-4 py-3 text-xs font-medium text-bleu-nuit uppercase tracking-wider">
                Statut
              </th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-100">
            <tr v-for="bailleur in bailleurs" :key="bailleur.id">
              <td class="px-4 py-3 text-sm font-medium text-slate-900">{{ bailleur.nom }}</td>
              <td class="px-4 py-3 text-sm text-slate-600">{{ bailleur.contact }}</td>
              <td class="px-4 py-3 text-sm text-slate-600">{{ bailleur.type }}</td>
              <td class="px-4 py-3 text-right text-sm text-slate-600">{{ bailleur.projets }}</td>
              <td class="px-4 py-3 text-right text-sm text-slate-600">{{ bailleur.finance }}</td>
              <td class="px-4 py-3">
                <span
                  class="inline-block px-2 py-1 text-xs font-medium rounded-full"
                  :class="
                    bailleur.statut === 'ReÃ§u'
                      ? 'text-emerald-700 bg-emerald-50'
                      : 'text-or bg-or/10'
                  "
                >
                  {{ bailleur.statut }}
                </span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Partenaires Table -->
    <div class="bg-white border border-slate-200/60 rounded-xl overflow-hidden">
      <div class="px-5 py-4 ">
        <h2 class="text-lg font-semibold text-slate-900">Partenaires</h2>
      </div>
      <div class="overflow-x-auto">
        <table class="w-full">
          <thead class="bg-slate-50">
            <tr>
              <th class="text-left px-4 py-3 text-xs font-medium text-bleu-nuit uppercase tracking-wider">
                Organisation
              </th>
              <th class="text-left px-4 py-3 text-xs font-medium text-bleu-nuit uppercase tracking-wider">
                Domaine
              </th>
              <th class="text-left px-4 py-3 text-xs font-medium text-bleu-nuit uppercase tracking-wider">
                Zone
              </th>
              <th class="text-left px-4 py-3 text-xs font-medium text-bleu-nuit uppercase tracking-wider">
                Projet
              </th>
              <th class="text-left px-4 py-3 text-xs font-medium text-bleu-nuit uppercase tracking-wider">
                Statut
              </th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-100">
            <tr v-for="partenaire in partenaires" :key="partenaire.id">
              <td class="px-4 py-3 text-sm font-medium text-slate-900">{{ partenaire.nom }}</td>
              <td class="px-4 py-3 text-sm text-slate-600">{{ partenaire.domaine }}</td>
              <td class="px-4 py-3 text-sm text-slate-600">{{ partenaire.zone }}</td>
              <td class="px-4 py-3 text-sm text-slate-600">{{ partenaire.projet }}</td>
              <td class="px-4 py-3">
                <span
                  class="inline-block px-2 py-1 text-xs font-medium rounded-full"
                  :class="
                    partenaire.statut === 'ACTIF'
                      ? 'text-emerald-700 bg-emerald-50'
                      : 'text-red-700 bg-red-50'
                  "
                >
                  {{ partenaire.statut }}
                </span>
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
  Users,
  Wallet,
  Activity,
} from "lucide-vue-next"
import { useGerantStore } from "@/modules/gerant/stores/gerantStore.js"

const store = useGerantStore()
const { formatMontant } = store

const statistiques = computed(() => store.statistiques)
const bailleurs = computed(() => store.bailleurs)
const partenaires = computed(() => store.partenaires)
</script>

