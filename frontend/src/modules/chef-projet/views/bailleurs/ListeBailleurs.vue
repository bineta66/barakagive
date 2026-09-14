<template>
  <div class="p-6 space-y-6 bg-white min-h-screen">
    <!-- En-tÃªte -->
    <div class="flex justify-between items-center  pb-4">
      <div>
        <h1 class="text-4xl font-bold text-or">Bailleurs</h1>
        <p class="text-xs text-gray-500 mt-1">
          GÃ©rez les bailleurs de fonds des missions humanitaires.
        </p>
      </div>

      <BoutonPrimary @click="alert('FonctionnalitÃ© Ã  venir')">
        <Plus :size="18" />
        Ajouter
      </BoutonPrimary>
    </div>

    <!-- Filtres -->
    <div class="bg-white border border-slate-200/60 shadow rounded-xl p-4 grid md:grid-cols-4 gap-3">
      <div class="relative">
        <Search class="absolute left-3 top-3 text-slate-400" :size="16" />
        <input
          v-model="recherche"
          type="text"
          placeholder="Rechercher par nom d'organisation..."
          class="w-full border rounded-lg pl-9 pr-3 py-2 text-sm"
        />
      </div>

      <select v-model="filtreStatut" class="border rounded-lg px-3 py-2 text-sm">
        <option>Tous les statuts</option>
        <option>ReÃ§u</option>
        <option>En attente</option>
      </select>

      <select class="border rounded-lg px-3 py-2 text-sm">
        <option>Tous les types</option>
        <option>International</option>
        <option>National</option>
      </select>

      <BoutonTertiary @click="reinitialiserFiltres">
        RÃ©initialiser
      </BoutonTertiary>
    </div>

    <!-- Section : Bailleurs de fonds -->
    <div class="space-y-4">
      <div class="bg-white px-4 py-3  inline-flex items-center gap-3">
        <Landmark :size="20" class="text-bleu-nuit" />
        <span class="text-base font-semibold text-slate-900">Bailleurs de fonds</span>
      </div>

      <div class="bg-white rounded-xl border border-slate-200/60 overflow-x-auto">
        <table class="w-full">
          <thead class="bg-slate-50 text-xs uppercase text-bleu-nuit">
            <tr>
              <th class="text-left px-4 py-3">ORGANISATION</th>
              <th class="text-left px-4 py-3">CONTACT INSTITUTIONNEL</th>
              <th class="text-center px-4 py-3">PROJETS ASSOCIÃ‰S</th>
              <th class="text-right px-4 py-3">FINANCEMENT ENGAGÃ‰</th>
              <th class="text-center px-4 py-3">ACTIONS</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="bailleur in bailleursFiltres" :key="bailleur.id" class="border-t hover:bg-slate-50">
              <td class="px-4 py-3">
                <p class="text-slate-900 text-sm font-semibold">{{ bailleur.nom }}</p>
              </td>
              <td class="px-4 py-3">
                <p class="text-zinc-700 text-xs">{{ bailleur.contact }}</p>
              </td>
              <td class="px-4 py-3 text-center">
                <p class="text-slate-900 text-xs font-medium">{{ bailleur.projets }}</p>
              </td>
              <td class="px-4 py-3 text-right">
                <p class="text-slate-900 text-sm font-semibold">{{ bailleur.finance }}</p>
              </td>
              <td class="px-4 py-3">
                <div class="flex justify-center gap-1.5">
                  <div class="size-7 bg-white flex justify-center items-center">
                    <Eye :size="14" class="text-bleu-nuit" />
                  </div>
                   <StatusBadge :statut="bailleur.statut">{{ bailleur.statut }}</StatusBadge>
                </div>
              </td>
            </tr>
          </tbody>
        </table>

        <div class="flex items-center justify-between px-4 py-3 border-t text-xs">
          <p class="text-slate-500">
            Affichage de 1 Ã  {{ bailleursFiltres.length }} sur 6 bailleurs
          </p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import StatusBadge from "@/components/ui/StatusBadge.vue"
import { ref, computed } from "vue"
import { Plus, Search, Eye, Landmark } from "lucide-vue-next"
import BoutonPrimary from "@/components/ui/BoutonPrimary.vue"
import BoutonTertiary from "@/components/ui/BoutonTertiary.vue"
import { bailleursMock } from "@/data/partenairesBailleursMock.js"

const recherche = ref("")
const filtreStatut = ref("Tous les statuts")

const bailleursFiltres = computed(() => {
  return bailleursMock.filter((b) => {
    const okRecherche = b.nom.toLowerCase().includes(recherche.value.toLowerCase()) ||
      b.contact.toLowerCase().includes(recherche.value.toLowerCase())
    const okStatut = filtreStatut.value === "Tous les statuts" || b.statut === filtreStatut.value
    return okRecherche && okStatut
  })
})

function reinitialiserFiltres() {
  recherche.value = ""
  filtreStatut.value = "Tous les statuts"
}
</script>

