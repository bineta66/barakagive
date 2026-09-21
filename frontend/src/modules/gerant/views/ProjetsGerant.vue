<template>
  <div class="p-6 space-y-6 bg-white min-h-screen">
    <!-- En-tête -->
    <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 pb-4 border-b border-slate-100">
      <div>
        <h1 class="text-3xl font-bold text-or">Gestion des Projets</h1>
        <p class="text-sm text-slate-500 mt-1">
          Créez, suivez et administrez les projets humanitaires de votre organisation.
        </p>
      </div>

      <div class="flex items-center gap-3">
        <router-link
          to="/gerant/projets/creer"
          class="inline-flex items-center gap-2 px-4 py-2.5 bg-bleu-nuit hover:bg-[#01111eff] text-white text-sm font-semibold rounded-lg shadow-xs transition"
        >
          <Plus :size="18" />
          Nouveau projet
        </router-link>

        <button
          @click="store.fetchProjets"
          class="px-4 py-2.5 bg-slate-100 hover:bg-slate-200 text-slate-700 text-sm font-medium rounded-lg transition"
        >
          Actualiser
        </button>
      </div>
    </div>

    <!-- Alert Message -->
    <AlertMessage v-if="feedback.message" :type="feedback.type" :message="feedback.message" class="mb-4" />

    <!-- KPI Cards -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
      <div class="bg-white border border-slate-200/60 shadow-xs-sm rounded-xl p-4 flex justify-between items-center">
        <div>
          <p class="text-xs font-bold uppercase text-slate-500">Total Projets</p>
          <h3 class="text-2xl font-bold text-or mt-1">{{ projets.length }}</h3>
        </div>
        <FolderKanban class="text-bleu-nuit" :size="28" />
      </div>

      <div class="bg-white border border-slate-200/60 shadow-xs-sm rounded-xl p-4 flex justify-between items-center">
        <div>
          <p class="text-xs font-bold uppercase text-slate-500">Projets Actifs</p>
          <h3 class="text-2xl font-bold text-emerald-600 mt-1">{{ projetsActifs.length }}</h3>
        </div>
        <Activity class="text-bleu-nuit" :size="28" />
      </div>

      <div class="bg-white border border-slate-200/60 shadow-xs-sm rounded-xl p-4 flex justify-between items-center">
        <div>
          <p class="text-xs font-bold uppercase text-slate-500">Enveloppe budgétaire</p>
          <h3 class="text-2xl font-bold text-or mt-1">{{ formatMontant(statistiques.budgetTotal) }} FCFA</h3>
        </div>
        <Wallet class="text-bleu-nuit" :size="28" />
      </div>
    </div>

    <!-- Filtres -->
    <div class="bg-white border border-slate-200/60 shadow-xs-sm rounded-xl p-4 flex flex-col sm:flex-row gap-3">
      <div class="relative flex-1">
        <Search class="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" :size="16" />
        <input
          v-model="search"
          type="text"
          placeholder="Rechercher par nom, code ou région..."
          class="w-full border border-slate-200 rounded-lg pl-9 pr-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-or/30"
        />
      </div>

      <select v-model="filtreRegion" class="border border-slate-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-or/30 bg-white">
        <option value="tous">Toutes les régions</option>
        <option v-for="r in regionsListe" :key="r" :value="r">{{ r }}</option>
      </select>
    </div>

    <!-- Loading State -->
    <LoadingSpinner v-if="loading" message="Chargement des projets..." />

    <!-- Tableau -->
    <div v-else class="bg-white rounded-xl border border-slate-200/60 overflow-hidden shadow-xs-sm">
      <EmptyState
        v-if="projetsFiltres.length === 0"
        titre="Aucun projet trouvé"
        description="Aucun projet ne correspond à vos filtres actuels. Cliquez sur 'Nouveau projet' pour en créer un."
      />

      <div v-else class="overflow-x-auto">
        <table class="w-full">
          <thead class="bg-slate-50 text-xs font-semibold uppercase text-bleu-nuit border-b border-slate-100">
            <tr>
              <th class="text-left px-4 py-3">Code & Projet</th>
              <th class="text-left px-4 py-3">Chef de projet</th>
              <th class="text-left px-4 py-3">Responsable Finance</th>
              <th class="text-left px-4 py-3">Région</th>
              <th class="text-right px-4 py-3">Budget</th>
              <th class="text-left px-4 py-3">Période</th>
              <th class="text-center px-4 py-3">Statut</th>
              <th class="text-right px-4 py-3">Actions</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-100 text-sm">
            <tr
              v-for="p in projetsFiltres"
              :key="p.id"
              class="hover:bg-slate-50/70 transition"
            >
              <td class="px-4 py-3.5">
                <div class="font-semibold text-slate-900">{{ p.name }}</div>
                <div class="text-xs font-medium text-or">{{ p.code || 'PRJ' }}</div>
              </td>
              <td class="px-4 py-3.5 text-slate-600 text-xs">
                {{ p.chef_projet || 'Non assigné' }}
              </td>
              <td class="px-4 py-3.5 text-slate-600 text-xs">
                {{ p.responsable_finance || 'Non assigné' }}
              </td>
              <td class="px-4 py-3.5 text-slate-600 text-xs">
                {{ p.region || '-' }}
              </td>
              <td class="px-4 py-3.5 text-right font-semibold text-slate-900 text-xs">
                {{ formatMontant(p.budget) }} FCFA
              </td>
              <td class="px-4 py-3.5 text-slate-500 text-xs">
                {{ p.start_date || '-' }} au {{ p.end_date || '-' }}
              </td>
              <td class="px-4 py-3.5 text-center">
                <span
                  class="inline-block px-2.5 py-1 text-xs font-semibold rounded-full"
                  :class="p.archived ? 'bg-slate-100 text-slate-600' : 'bg-emerald-50 text-emerald-700'"
                >
                  {{ p.archived ? 'Archivé' : 'En cours' }}
                </span>
              </td>
              <td class="px-4 py-3.5 text-right">
                <div class="flex justify-end gap-1">
                  <RouterLink
                    :to="`/gerant/projets/${p.id}`"
                    class="text-slate-400 hover:text-bleu-nuit transition p-1"
                    title="Voir les détails"
                  >
                    <Eye :size="16" />
                  </RouterLink>

                  <RouterLink
                    v-if="!p.archived"
                    :to="`/gerant/projets/modifier/${p.id}`"
                    class="text-slate-400 hover:text-or transition p-1"
                    title="Modifier"
                  >
                    <Pencil :size="16" />
                  </RouterLink>

                  <button
                    v-if="!p.archived"
                    @click="archiverProjet(p.id)"
                    class="text-slate-400 hover:text-red-600 transition p-1"
                    title="Archiver ce projet"
                  >
                    <Trash2 :size="16" />
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, reactive, onMounted } from "vue"
import {
  FolderKanban,
  Activity,
  Wallet,
  Search,
  Plus,
  Eye,
  Pencil,
  Trash2,
} from "lucide-vue-next"
import { RouterLink } from "vue-router"
import { useGerantStore } from "@/modules/gerant/stores/gerantStore.js"
import LoadingSpinner from "@/components/ui/LoadingSpinner.vue"
import EmptyState from "@/components/ui/EmptyState.vue"
import AlertMessage from "@/components/ui/AlertMessage.vue"

const store = useGerantStore()
const search = ref("")
const filtreRegion = ref("tous")
const loading = ref(false)
const feedback = reactive({ type: "success", message: "" })

const projets = computed(() => store.projets)
const statistiques = computed(() => store.statistiques)
const formatMontant = store.formatMontant

const projetsActifs = computed(() => projets.value.filter((p) => !p.archived))

const regionsListe = computed(() => {
  const regions = projets.value.map((p) => p.region).filter(Boolean)
  return [...new Set(regions)]
})

const projetsFiltres = computed(() => {
  return projets.value.filter((p) => {
    const q = search.value.toLowerCase()
    const matchesSearch =
      !q ||
      (p.name && p.name.toLowerCase().includes(q)) ||
      (p.code && p.code.toLowerCase().includes(q)) ||
      (p.region && p.region.toLowerCase().includes(q))

    const matchesRegion =
      filtreRegion.value === "tous" || p.region === filtreRegion.value

    return matchesSearch && matchesRegion
  })
})

const archiverProjet = async (id) => {
  if (!confirm("Voulez-vous vraiment archiver ce projet ?")) return
  feedback.message = ""
  try {
    await store.deleteProject(id)
    feedback.type = "success"
    feedback.message = "Projet archivé avec succès."
  } catch (err) {
    feedback.type = "error"
    feedback.message = "Erreur lors de l'archivage du projet."
  }
}

onMounted(async () => {
  loading.value = true
  try {
    await store.fetchProjets()
  } finally {
    loading.value = false
  }
})
</script>
