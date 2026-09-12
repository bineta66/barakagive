<template>
  <div class="p-6 space-y-6 bg-white min-h-screen">
    <!-- Titre -->
    <div class="flex justify-between items-center border-b border-slate-200 pb-4">
      <div>
        <h1 class="text-4xl font-bold text-amber-800">Campagnes</h1>
        <p class="text-xs text-gray-500 mt-1">
          Gérez et suivez les campagnes humanitaires.
        </p>
      </div>

      <BoutonPrimary to="/chef-projet/campagnes/creer">
        <Plus :size="18" />
        Nouvelle campagne
      </BoutonPrimary>
    </div>

    <!-- Cartes statistiques -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
      <div class="bg-white border border-slate-200/60 rounded-xl p-4 flex justify-between">
        <div>
          <p class="text-xs font-bold uppercase text-slate-900">Total campagnes</p>
          <h3 class="text-xl font-bold text-sky-900 mt-2">{{ statistiques.total }}</h3>
        </div>
        <ClipboardList class="text-slate-400" :size="28" />
      </div>

      <div class="bg-white border border-slate-200/60 rounded-xl p-4 flex justify-between">
        <div>
          <p class="text-xs font-bold uppercase text-slate-900">Actives</p>
          <h3 class="text-xl font-bold text-amber-800 mt-2">{{ statistiques.actives }}</h3>
        </div>
        <Activity class="text-slate-400" :size="28" />
      </div>

      <div class="bg-white border border-slate-200/60 rounded-xl p-4 flex justify-between">
        <div>
          <p class="text-xs font-bold uppercase text-slate-900">Terminées</p>
          <h3 class="text-xl font-bold text-emerald-700 mt-2">{{ statistiques.terminees }}</h3>
        </div>
        <CheckCircle class="text-slate-400" :size="28" />
      </div>
    </div>

    <!-- Filtres -->
    <div class="bg-white border border-slate-200/60 rounded-xl p-4 grid md:grid-cols-4 gap-3">
      <div class="relative">
        <Search class="absolute left-3 top-3 text-slate-400" :size="16" />
        <input
          :value="recherche"
          @input="$emit('update:recherche', $event.target.value)"
          type="text"
          placeholder="Rechercher une campagne..."
          class="w-full border rounded-lg pl-9 pr-3 py-2 text-sm"
        />
      </div>

      <select
        :value="filtreStatut"
        @change="$emit('update:filtreStatut', $event.target.value)"
        class="border rounded-lg px-3 py-2 text-sm"
      >
        <option>Tous les statuts</option>
        <option>En cours</option>
        <option>Planifiée</option>
        <option>Terminée</option>
      </select>

      <select
        :value="filtreProjet"
        @change="$emit('update:filtreProjet', $event.target.value)"
        class="border rounded-lg px-3 py-2 text-sm"
      >
        <option>Tous les projets</option>
        <option>Projet Santé</option>
        <option>Projet Nutrition</option>
        <option>Projet Eau</option>
        <option>Projet Education</option>
      </select>

      <select
        :value="filtreZone"
        @change="$emit('update:filtreZone', $event.target.value)"
        class="border rounded-lg px-3 py-2 text-sm"
      >
        <option>Toutes les zones</option>
        <option>Dakar</option>
        <option>Louga</option>
        <option>Kolda</option>
        <option>Matam</option>
        <option>Thiès</option>
      </select>
    </div>

    <!-- Tableau -->
    <div class="bg-white rounded-xl border border-slate-200/60 overflow-hidden">
      <table class="w-full">
        <thead class="bg-slate-50 text-xs uppercase text-sky-900">
          <tr>
            <th class="text-left px-4 py-4">Campagne</th>
            <th class="text-left px-4">Projet</th>
            <th class="text-left px-4">Zone</th>
            <th class="text-left px-4">Statut</th>
            <th class="text-right px-4">Actions</th>
          </tr>
        </thead>

        <tbody>
          <tr v-for="campagne in campagnesPage" :key="campagne.id" class="border-t hover:bg-slate-50">
            <td class="px-4 py-4">
              <h3 class="font-semibold text-sm text-slate-800">
                {{ campagne.nom }}
              </h3>
              <p class="text-xs text-gray-500">{{ campagne.code }}</p>
            </td>

            <td class="px-4 text-sm text-slate-600">
              {{ campagne.projet }}
            </td>

            <td class="px-4 text-sm text-slate-600">
              {{ campagne.zone }}
            </td>

            <td class="px-4">
              <span
                class="px-2 py-1 rounded text-xs font-semibold"
                :class="{
                  'bg-emerald-100 text-emerald-700': campagne.statut === 'En cours',
                  'bg-gray-100 text-gray-600': campagne.statut === 'Planifiée',
                  'bg-sky-100 text-sky-700': campagne.statut === 'Terminée',
                }"
              >
                {{ campagne.statut }}
              </span>
            </td>

            <td class="px-4">
              <div class="flex justify-end gap-2">
                <RouterLink :to="`/chef-projet/campagnes/${campagne.id}`" class="text-slate-500 hover:text-sky-900">
                  <Eye :size="18" />
                </RouterLink>

                <RouterLink :to="`/chef-projet/campagnes/modifier/${campagne.id}`" class="text-slate-500 hover:text-amber-700">
                  <Pencil :size="18" />
                </RouterLink>

                <RouterLink :to="`/chef-projet/campagnes/${campagne.id}/formulaire`" class="text-slate-500 hover:text-sky-900" title="Formulaire">
                  <FileText :size="18" />
                </RouterLink>

                <button class="text-slate-500 hover:text-red-600">
                  <Archive :size="18" />
                </button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>

      <!-- Pagination -->
      <div class="flex items-center justify-between px-4 py-3 border-t text-xs">
        <p class="text-slate-500">
          Affichage de 1 à {{ campagnesPage.length }} sur {{ campagnesFiltrees.length }} campagnes
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
            :class="page === pageCourante ? 'bg-sky-900 text-white' : ''"
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
import { useCampagnes } from "@/composables/useCampagnes.js"
import { Plus, ClipboardList, Activity, CheckCircle, Search, Eye, Pencil, Archive, FileText } from "lucide-vue-next"
import BoutonPrimary from "@/components/ui/BoutonPrimary.vue"

const {
  recherche,
  filtreStatut,
  filtreProjet,
  filtreZone,
  pageCourante,
  campagnesPage,
  totalPages,
  campagnesFiltrees,
  statistiques,
  reinitialiserFiltres,
} = useCampagnes()
</script>
