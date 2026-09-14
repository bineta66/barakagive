<template>
  <div class="p-6 space-y-6 bg-white min-h-screen">
    <!-- En-tÃªte -->
    <div class="flex justify-between items-center  pb-4">
      <div>
        <h1 class="text-4xl font-bold text-or">Partenaires</h1>
        <p class="text-xs text-gray-500 mt-1">
          Suivez les organisations partenaires opÃ©rationnelles et locales des missions humanitaires.
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
        <option>ACTIF</option>
        <option>INACTIF</option>
      </select>

      <select class="border rounded-lg px-3 py-2 text-sm">
        <option>Tous les domaines</option>
        <option>Secours d'Urgence & SantÃ©</option>
        <option>Cliniques Mobiles & PÃ©diatrie</option>
        <option>Forages Solaires & Assainissement</option>
      </select>

      <BoutonTertiary @click="reinitialiserFiltres">
        RÃ©initialiser
      </BoutonTertiary>
    </div>

    <!-- Section : Partenaires OpÃ©rationnels & Locaux -->
    <div class="space-y-4">
      <div class="bg-white px-4 py-3  inline-flex items-center gap-3">
        <Users :size="20" class="text-bleu-nuit" />
        <span class="text-base font-semibold text-slate-900">Partenaires OpÃ©rationnels & Locaux</span>
      </div>

      <div class="bg-white rounded-xl border border-slate-200/60 overflow-x-auto">
        <table class="w-full">
          <thead class="bg-slate-50 text-xs uppercase text-bleu-nuit">
            <tr>
              <th class="text-left px-4 py-3">ORGANISATION</th>
              <th class="text-left px-4 py-3">DOMAINE D'INTERVENTION</th>
              <th class="text-left px-4 py-3">ZONE DE DÃ‰PLOIEMENT</th>
              <th class="text-center px-4 py-3">STATUT OPÃ‰RATIONNEL</th>
              <th class="text-center px-4 py-3">ACTIONS</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="partenaire in partenairesFiltres" :key="partenaire.id" class="border-t hover:bg-slate-50">
              <td class="px-4 py-3">
                <p class="text-slate-900 text-sm font-semibold">{{ partenaire.nom }}</p>
              </td>
              <td class="px-4 py-3">
                <p class="text-slate-900 text-xs">{{ partenaire.domaine }}</p>
              </td>
              <td class="px-4 py-3">
                <p class="text-slate-900 text-xs">{{ partenaire.zone }}</p>
              </td>
              <td class="px-4 py-3 text-center">
                <StatusBadge :statut="partenaire.statut">{{ partenaire.statut }}</StatusBadge>
              </td>
              <td class="px-4 py-3">
                <div class="flex justify-center gap-1.5">
                  <div class="size-7 bg-indigo-50 flex justify-center items-center">
                    <Pencil :size="14" class="text-bleu-nuit" />
                  </div>
                  <div class="size-7 bg-indigo-50 flex justify-center items-center">
                    <Trash2 :size="14" class="text-bleu-nuit" />
                  </div>
                </div>
              </td>
            </tr>
          </tbody>
        </table>

        <div class="flex items-center justify-between px-4 py-3 border-t text-xs">
          <p class="text-slate-500">
            Affichage de 1 Ã  {{ partenairesFiltres.length }} sur 6 partenaires
          </p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import StatusBadge from "@/components/ui/StatusBadge.vue"
import { ref, computed } from "vue"
import { Plus, Search, Users, Pencil, Trash2 } from "lucide-vue-next"
import BoutonPrimary from "@/components/ui/BoutonPrimary.vue"
import BoutonTertiary from "@/components/ui/BoutonTertiary.vue"
import { partenairesMock } from "@/data/partenairesBailleursMock.js"

const recherche = ref("")
const filtreStatut = ref("Tous les statuts")

const partenairesFiltres = computed(() => {
  return partenairesMock.filter((p) => {
    const okRecherche = p.nom.toLowerCase().includes(recherche.value.toLowerCase())
    const okStatut = filtreStatut.value === "Tous les statuts" || p.statut === filtreStatut.value
    return okRecherche && okStatut
  })
})

function reinitialiserFiltres() {
  recherche.value = ""
  filtreStatut.value = "Tous les statuts"
}
</script>

