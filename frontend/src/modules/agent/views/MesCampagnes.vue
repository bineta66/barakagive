<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-2xl font-bold text-slate-900">Mes campagnes</h1>
        <p class="text-sm text-slate-500 mt-1">
          Suivi dÃ©taillÃ© de vos campagnes de terrain
        </p>
      </div>
      <div class="flex gap-2">
        <input
          v-model="search"
          type="text"
          placeholder="Rechercher une campagne..."
          class="px-3 py-2 text-sm border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-or/30 w-64"
        />
      </div>
    </div>

    <!-- Table -->
    <div class="bg-white border border-slate-200/60 rounded-xl overflow-hidden">
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
                Date
              </th>
              <th class="text-left px-4 py-3 text-xs font-medium text-bleu-nuit uppercase tracking-wrier">
                Statut
              </th>
              <th class="text-left px-4 py-3 text-xs font-medium text-bleu-nuit uppercase tracking-wider">
                Collecte
              </th>
              <th class="text-left px-4 py-3 text-xs font-medium text-bleu-nuit uppercase tracking-wider">
                Objectif
              </th>
              <th class="text-left px-4 py-3 text-xs font-medium text-bleu-nuit uppercase tracking-wider">
                Action
              </th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-100">
            <tr v-for="campagne in campagnesFiltrees" :key="campagne.id">
              <td class="px-4 py-3 text-sm font-medium text-slate-900">
                {{ campagne.nom }}
              </td>
              <td class="px-4 py-3 text-sm text-slate-600">{{ campagne.ONG }}</td>
              <td class="px-4 py-3 text-sm text-slate-600">{{ campagne.zone }}</td>
              <td class="px-4 py-3 text-sm text-slate-500">
                {{ campagne.dateDebut }} Ã¢â€ â€™ {{ campagne.dateFin }}
              </td>
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
              <td class="px-4 py-3">
                <button
                  @click="voirCampagne(campagne.id)"
                  class="text-xs text-bleu-nuit hover:text-[#01111eff] font-medium"
                >
                  Voir dÃ©tails
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from "vue"
import { useAgentStore } from "@/modules/agent/stores/agentStore.js"

const store = useAgentStore()
const { campagnes, formatMontant } = store

const search = ref("")

const campagnesFiltrees = computed(() => {
  if (!search.value) return campagnes.value
  return campagnes.value.filter(
    (c) =>
      c.nom.toLowerCase().includes(search.value.toLowerCase()) ||
      c.ONG.toLowerCase().includes(search.value.toLowerCase())
  )
})

const voirCampagne = (id) => {
  console.log("Voir la campagne:", id)
}
</script>





