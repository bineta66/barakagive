<template>
  <div class="space-y-6 max-w-6xl mx-auto p-4 sm:p-6">
    <!-- Header -->
    <div class="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
      <div>
        <h1 class="text-2xl font-bold text-slate-900">Mes campagnes de collecte</h1>
        <p class="text-sm text-slate-500 mt-1">
          Consultez les campagnes actives et accédez aux formulaires de recensement
        </p>
      </div>
      <div class="w-full sm:w-auto">
        <input
          v-model="search"
          type="text"
          placeholder="Rechercher une campagne..."
          class="w-full sm:w-64 px-3 py-2 text-sm border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-or/30 bg-white"
        />
      </div>
    </div>

    <LoadingSpinner v-if="campaignStore.loading && !campaignStore.campaigns.length" message="Chargement des campagnes..." />
    <AlertMessage v-if="error" type="error" :message="error" class="mb-4" />

    <!-- Table -->
    <div class="bg-white border border-slate-200/60 rounded-xl overflow-hidden shadow-xs-sm">
      <div class="overflow-x-auto">
        <table class="w-full">
          <thead class="bg-slate-50 border-b border-slate-200 text-xs font-semibold text-bleu-nuit uppercase tracking-wider">
            <tr>
              <th class="text-left px-5 py-3.5">Campagne</th>
              <th class="text-left px-5 py-3.5">Projet</th>
              <th class="text-left px-5 py-3.5">Période</th>
              <th class="text-left px-5 py-3.5">Statut</th>
              <th class="text-right px-5 py-3.5">Action</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-100 text-sm">
            <tr v-for="campagne in campagnesFiltrees" :key="campagne.id" class="hover:bg-slate-50 transition">
              <td class="px-5 py-4">
                <span class="font-semibold text-slate-900">{{ campagne.nom }}</span>
                <p class="text-xs text-slate-400 font-mono">{{ campagne.code_campagne }}</p>
              </td>
              <td class="px-5 py-4 text-slate-600">{{ campagne.projet?.name || "-" }}</td>
              <td class="px-5 py-4 text-slate-500 text-xs">
                {{ campagne.date_debut || "-" }} au {{ campagne.date_fin || "-" }}
              </td>
              <td class="px-5 py-4">
                <span
                  class="inline-block px-2.5 py-1 text-xs font-semibold rounded-full"
                  :class="
                    campagne.statut === 'En cours'
                      ? 'text-emerald-700 bg-emerald-50'
                      : 'text-slate-700 bg-slate-100'
                  "
                >
                  {{ campagne.statut }}
                </span>
              </td>
              <td class="px-5 py-4 text-right">
                <router-link
                  :to="`/agent/collecte?campagne=${campagne.id}`"
                  class="inline-flex items-center gap-1.5 px-3 py-1.5 bg-bleu-nuit text-white text-xs font-semibold rounded-lg hover:bg-[#01111eff] transition"
                >
                  <UserPlus :size="14" />
                  Collecter
                </router-link>
              </td>
            </tr>

            <tr v-if="campagnesFiltrees.length === 0">
              <td colspan="5" class="px-5 py-8 text-center text-sm text-slate-500">
                Aucune campagne trouvée.
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from "vue"
import { UserPlus } from "lucide-vue-next"
import LoadingSpinner from "@/components/ui/LoadingSpinner.vue"
import AlertMessage from "@/components/ui/AlertMessage.vue"
import { useCampaignStore } from "@/stores/campaign.js"

const campaignStore = useCampaignStore()
const search = ref("")
const error = ref(null)

onMounted(async () => {
  try {
    await campaignStore.fetchCampaigns()
  } catch (err) {
    error.value = "Impossible de charger les campagnes."
  }
})

const determineStatut = (c) => {
  const today = new Date().toISOString().split("T")[0]
  if (c.date_debut && c.date_debut > today) return "Planifiée"
  if (c.date_fin && c.date_fin < today) return "Terminée"
  return "En cours"
}

const campagnesFiltrees = computed(() => {
  return campaignStore.campaigns
    .map((c) => ({
      ...c,
      statut: determineStatut(c),
    }))
    .filter((c) => {
      const q = search.value.toLowerCase()
      if (!q) return true
      return (
        (c.nom || "").toLowerCase().includes(q) ||
        (c.code_campagne || "").toLowerCase().includes(q) ||
        (c.projet?.name || "").toLowerCase().includes(q)
      )
    })
})
</script>

