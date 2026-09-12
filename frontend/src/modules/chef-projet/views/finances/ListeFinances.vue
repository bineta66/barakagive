<template>
  <div class="p-6 space-y-6 bg-white min-h-screen">
    <!-- Titre -->
    <div class="flex justify-between items-center border-b border-slate-200 pb-4">
      <div>
        <h1 class="text-4xl font-bold text-amber-800">Finances</h1>
        <p class="text-xs text-gray-500 mt-1">
          Suivi budgétaire et exécutive des projets humanitaires.
        </p>
      </div>
    </div>

    <!-- Cartes statistiques -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
      <div class="bg-white border border-slate-200/60 rounded-xl p-4 flex justify-between">
        <div>
          <p class="text-xs font-bold uppercase text-slate-900">Volume budgétaire alloué</p>
          <h3 class="text-xl font-bold text-sky-900 mt-2">{{ formatMontant(statistiques.budgetTotal) }} FCFA</h3>
        </div>
        <Wallet class="text-slate-400" :size="28" />
      </div>

      <div class="bg-white border border-slate-200/60 rounded-xl p-4 flex justify-between">
        <div>
          <p class="text-xs font-bold uppercase text-slate-900">Taux d'exécution</p>
          <h3 class="text-xl font-bold text-amber-800 mt-2">{{ statistiques.tauxExecution }} %</h3>
        </div>
        <Activity class="text-slate-400" :size="28" />
      </div>

      <div class="bg-white border border-slate-200/60 rounded-xl p-4 flex justify-between">
        <div>
          <p class="text-xs font-bold uppercase text-slate-900">Montant restant</p>
          <h3 class="text-xl font-bold text-emerald-700 mt-2">{{ formatMontant(statistiques.totalRestant) }} FCFA</h3>
        </div>
        <PiggyBank class="text-slate-400" :size="28" />
      </div>
    </div>

    <!-- Filtres -->
    <div class="bg-white border border-slate-200/60 rounded-xl p-4 grid md:grid-cols-4 gap-3">
      <div class="relative">
        <Search class="absolute left-3 top-3 text-slate-400" :size="16" />
        <input
          v-model="recherche"
          type="text"
          placeholder="Rechercher un projet..."
          class="w-full border rounded-lg pl-9 pr-3 py-2 text-sm"
        />
      </div>

      <select v-model="filtreStatut" class="border rounded-lg px-3 py-2 text-sm">
        <option>Tous les statuts</option>
        <option>En cours</option>
        <option>Terminée</option>
        <option>Planifiée</option>
      </select>

      <select v-model="filtreProjet" class="border rounded-lg px-3 py-2 text-sm">
        <option>Tous les projets</option>
        <option v-for="projet in projets" :key="projet.id" :value="projet.nom">{{ projet.nom }}</option>
      </select>

      <select v-model="filtreRegion" class="border rounded-lg px-3 py-2 text-sm">
        <option>Toutes les régions</option>
        <option v-for="region in regions" :key="region" :value="region">{{ region }}</option>
      </select>
    </div>

    <!-- Tableau -->
    <div class="bg-white rounded-xl border border-slate-200/60 overflow-hidden">
      <table class="w-full">
        <thead class="bg-slate-50 text-xs uppercase text-sky-900">
          <tr>
            <th class="text-left px-4 py-4">Projet</th>
            <th class="text-right px-4">Budget alloué</th>
            <th class="text-right px-4">Engagé</th>
            <th class="text-right px-4">Restant</th>
            <th class="text-left px-4">Statut</th>
            <th class="text-right px-4">Actions</th>
          </tr>
        </thead>

        <tbody>
            <tr
            v-for="projet in financesPage"
            :key="projet.code"
            class="border-t hover:bg-slate-50"
          >
            <td class="px-4 py-4">
              <h3 class="font-semibold text-sm text-slate-800">
                {{ projet.nom }}
              </h3>
              <p class="text-xs text-gray-500">{{ projet.code }}</p>
            </td>

            <td class="px-4 text-right text-sm font-semibold">
              {{ formatMontant(projet.budgetAllocation) }} FCFA
            </td>

            <td class="px-4 text-right text-sm text-slate-600">
              {{ formatMontant(projet.montantEngage) }} FCFA
            </td>

            <td class="px-4 text-right text-sm text-slate-600">
              {{ formatMontant(projet.budgetAllocation - projet.montantEngage) }} FCFA
            </td>

            <td class="px-4">
              <StatutProjet :status="projet.statut" />
            </td>

            <td class="px-4">
              <div class="flex justify-end gap-2">
                <RouterLink :to="`/chef-projet/finances/${projet.id}`" class="text-slate-500 hover:text-sky-700">
                  <Eye :size="18" />
                </RouterLink>
              </div>
            </td>
          </tr>
        </tbody>
      </table>

      <!-- Pagination -->
      <div class="flex items-center justify-between px-4 py-3 border-t text-xs">
        <p class="text-slate-500">
          Affichage de 1 à {{ financesPage.length }} sur {{ financesFiltrees.length }} projets
        </p>

        <div class="flex gap-1">
          <button
            class="px-3 py-2 border rounded bg-slate-100 text-slate-400"
            :disabled="pageCourante === 1"
            @click="pageCourante = pageCourante - 1"
          >
            Précédent
          </button>

          <button
            v-for="page in totalPages"
            :key="page"
            class="w-8 h-8 border rounded"
            :class="page === pageCourante ? 'bg-green-900 text-white' : ''"
            @click="pageCourante = page"
          >
            {{ page }}
          </button>

          <button
            class="px-3 py-2 border rounded"
            :disabled="pageCourante === totalPages"
            @click="pageCourante = pageCourante + 1"
          >
            Suivant
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from "vue"
import { Wallet, Activity, PiggyBank, Search, Eye } from "lucide-vue-next"
import { RouterLink } from "vue-router"
import StatutProjet from "@/modules/chef-projet/components/projets/StatutProjet.vue"
import { useFinances } from "@/composables/useFinances.js"

const {
  recherche,
  filtreStatut,
  filtreProjet,
  filtreRegion,
  pageCourante,
  financesPage,
  financesFiltrees,
  totalPages,
  statistiques,
  projets,
  regions,
  reinitialiserFiltres,
} = useFinances()

watch([recherche, filtreStatut, filtreProjet, filtreRegion], () => {
  pageCourante.value = 1
})

function formatMontant(montant) {
  if (!montant) return "0"
  return montant.toLocaleString("fr-FR")
}
</script>
