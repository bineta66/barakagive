<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-2xl font-bold text-slate-900">Synchronisation</h1>
        <p class="text-sm text-slate-500 mt-1">
          GÃ©rer la synchronisation des donnÃ©es terrain avec le serveur
        </p>
      </div>
      <button
        @click="syncAll"
        class="px-4 py-2 bg-bleu-nuit text-white rounded-lg hover:bg-[#01111eff] transition flex items-center gap-2"
      >
        <RefreshCw :size="16" />
        <span>Synchroniser tout</span>
      </button>
    </div>

    <!-- Sync Status -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-5">
      <StatCard
        titre="Ã‰lÃ©ments synchronisÃ©s"
        :valeur="statistiques.elementsSynchronises"
        :icone="CheckCircle"
        couleur="emerald"
      />
      <StatCard
        titre="En attente de sync"
        :valeur="statistiques.elementsEnAttente"
        :icone="Clock"
        couleur="orange"
      />
      <StatCard
        titre="DerniÃ¨re sync"
        valeur="2025-09-12 14:30"
        :icone="Cloud"
        couleur="blue"
      />
    </div>

    <!-- Offline Data -->
    <div class="bg-white border border-slate-200/60 rounded-xl">
      <div class="px-5 py-4 ">
        <h2 class="text-lg font-semibold text-slate-900">
          DonnÃ©es en mode hors ligne
        </h2>
      </div>
      <div class="overflow-x-auto">
        <table class="w-full">
          <thead class="bg-slate-50">
            <tr>
              <th class="text-left px-4 py-3 text-xs font-medium text-bleu-nuit uppercase tracking-wider">
                Date
              </th>
              <th class="text-left px-4 py-3 text-xs font-medium text-bleu-nuit uppercase tracking-wider">
                Campagne
              </th>
              <th class="text-left px-4 py-3 text-xs font-medium text-bleu-nuit uppercase tracking-wider">
                Zone
              </th>
              <th class="text-left px-4 py-3 text-xs font-medium text-bleu-nuit uppercase tracking-wider">
                Montant
              </th>
              <th class="text-left px-4 py-3 text-xs font-medium text-bleu-nuit uppercase tracking-wider">
                Statut
              </th>
              <th class="text-left px-4 py-3 text-xs font-medium text-bleu-nuit uppercase tracking-wider">
                Action
              </th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-100">
            <tr v-for="collecte in collectesEnAttente" :key="collecte.id">
              <td class="px-4 py-3 text-sm text-slate-600">{{ collecte.date }}</td>
              <td class="px-4 py-3 text-sm font-medium text-slate-900">
                {{ collecte.campagne }}
              </td>
              <td class="px-4 py-3 text-sm text-slate-600">{{ collecte.zone }}</td>
              <td class="px-4 py-3 text-sm text-slate-900">
                {{ formatMontant(collecte.montant) }} FCFA
              </td>
              <td class="px-4 py-3">
                <span
                  class="inline-block px-2 py-1 text-xs font-medium text-orange-700 bg-orange-50 rounded-full"
                >
                  {{ collecte.statut }}
                </span>
              </td>
              <td class="px-4 py-3">
                <button
                  @click="synchroniserElement(collecte.id)"
                  class="text-xs text-bleu-nuit hover:text-[#01111eff] font-medium"
                >
                  Synchroniser
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
import { computed } from "vue"
import { useAgentStore } from "@/modules/agent/stores/agentStore.js"
import { CheckCircle, Clock, Cloud, RefreshCw } from "lucide-vue-next"
import StatCard from "@/components/ui/StatCard.vue"

const store = useAgentStore()
const { collectes, statistiques, formatMontant } = store

const collectesEnAttente = computed(() => {
  return collectes.value.filter((c) => c.statut === "En attente de sync")
})

const syncAll = () => {
  console.log("Synchronisation de toutes les donnÃ©es...")
}

const synchroniserElement = (id) => {
  console.log("Synchroniser l'Ã©lÃ©ment:", id)
}
</script>





