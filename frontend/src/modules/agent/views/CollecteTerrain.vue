<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-2xl font-bold text-slate-900">Collecte sur le terrain</h1>
        <p class="text-sm text-slate-500 mt-1">
          Saisir et suivre les collectes effectuÃ©es sur le terrain
        </p>
      </div>
      <button
        @click="showForm = true"
        class="px-4 py-2 bg-bleu-nuit text-white rounded-lg hover:bg-[#01111eff] transition flex items-center gap-2"
      >
        <Plus :size="16" />
        <span>Nouvelle collecte</span>
      </button>
    </div>

    <!-- Filter -->
    <div class="flex gap-2">
      <select
        v-model="filtreStatut"
        class="px-3 py-2 text-sm border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-or/30"
      >
        <option value="tous">Tous les statuts</option>
        <option value="SynchronisÃ©">SynchronisÃ©s</option>
        <option value="En attente de sync">En attente</option>
      </select>
    </div>

    <!-- Table -->
    <div class="bg-white border border-slate-200/60 rounded-xl overflow-hidden">
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
            <tr v-for="collecte in collectesFiltrees" :key="collecte.id">
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
                  class="inline-block px-2 py-1 text-xs font-medium rounded-full"
                  :class="
                    collecte.statut === 'SynchronisÃ©'
                      ? 'text-emerald-700 bg-emerald-50'
                      : 'text-orange-700 bg-orange-50'
                  "
                >
                  {{ collecte.statut }}
                </span>
              </td>
              <td class="px-4 py-3">
                <button
                  v-if="collecte.statut !== 'SynchronisÃ©'"
                  @click="synchroniser(collecte.id)"
                  class="text-xs text-bleu-nuit hover:text-[#01111eff] font-medium"
                >
                  Synchroniser
                </button>
                <span
                  v-else
                  class="text-xs text-slate-400"
                >
                  â€”
                </span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Modal -->
    <AgentCollecteFormModal
      v-if="showForm"
      @close="showForm = false"
    />
  </div>
</template>

<script setup>
import { ref, computed } from "vue"
import { useAgentStore } from "@/modules/agent/stores/agentStore.js"
import { Plus } from "lucide-vue-next"
import AgentCollecteFormModal from "@/modules/agent/components/AgentCollecteFormModal.vue"

const store = useAgentStore()
const { collectes, formatMontant } = store

const showForm = ref(false)
const filtreStatut = ref("tous")

const collectesFiltrees = computed(() => {
  if (filtreStatut.value === "tous") return collectes.value
  return collectes.value.filter((c) => c.statut === filtreStatut.value)
})

const synchroniser = (id) => {
  console.log("Synchroniser la collecte:", id)
}
</script>





