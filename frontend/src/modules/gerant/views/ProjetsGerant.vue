<template>
  <div class="p-6 space-y-6 bg-white min-h-screen">
    <!-- En-tÃªte -->
    <div class="flex justify-between items-center  pb-4">
      <div>
        <h1 class="text-4xl font-bold text-or">Projets</h1>
        <p class="text-xs text-gray-500 mt-1">
          GÃ©rez les projets humanitaires et leurs Ã©quipes.
        </p>
      </div>
      <BoutonPrimary to="/gerant/projets/creer">
        <Plus class="w-5 h-5" />
        Nouveau projet
      </BoutonPrimary>
    </div>

    <!-- KPI Cards -->
    <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
      <div class="bg-white border border-slate-200/60 shadow rounded-xl p-4 flex justify-between">
        <div>
          <p class="text-xs font-bold uppercase text-slate-900">Projets actifs</p>
          <h3 class="text-xl font-bold text-or mt-2">{{ projetsActifs }}</h3>
        </div>
        <FolderKanban class="text-bleu-nuit" :size="28" />
      </div>

      <div class="bg-white border border-slate-200/60 shadow rounded-xl p-4 flex justify-between">
        <div>
          <p class="text-xs font-bold uppercase text-slate-900">En cours</p>
          <h3 class="text-xl font-bold text-or mt-2">{{ projetsEnCours }}</h3>
        </div>
        <Activity class="text-bleu-nuit" :size="28" />
      </div>

      <div class="bg-white border border-slate-200/60 shadow rounded-xl p-4 flex justify-between">
        <div>
          <p class="text-xs font-bold uppercase text-slate-900">PlanifiÃ©s</p>
          <h3 class="text-xl font-bold text-or mt-2">{{ projetsPlanifies }}</h3>
        </div>
        <Calendar class="text-bleu-nuit" :size="28" />
      </div>

      <div class="bg-white border border-slate-200/60 shadow rounded-xl p-4 flex justify-between">
        <div>
          <p class="text-xs font-bold uppercase text-slate-900">Budget total</p>
          <h3 class="text-xl font-bold text-or mt-2">{{ formatMontant(budgetTotal) }} FCFA</h3>
        </div>
        <Wallet class="text-bleu-nuit" :size="28" />
      </div>
    </div>

    <!-- Filtres -->
    <div class="bg-white border border-slate-200/60 shadow rounded-xl p-4 grid md:grid-cols-4 gap-3">
      <div class="relative">
        <Search class="absolute left-3 top-3 text-slate-400" :size="16" />
        <input
          v-model="search"
          type="text"
          placeholder="Rechercher un projet..."
          class="w-full border rounded-lg pl-9 pr-3 py-2 text-sm"
        />
      </div>

      <select v-model="filtreStatut" class="border rounded-lg px-3 py-2 text-sm">
        <option>Tous les statuts</option>
        <option v-for="s in statutsListe" :key="s" :value="s">{{ s }}</option>
      </select>

      <select v-model="filtreRegion" class="border rounded-lg px-3 py-2 text-sm">
        <option>Toutes les rÃ©gions</option>
        <option v-for="r in regionsListe" :key="r" :value="r">{{ r }}</option>
      </select>

      <BoutonTertiary @click="resetFilters">
        RÃ©initialiser
      </BoutonTertiary>
    </div>

    <!-- Tableau -->
    <div class="bg-white rounded-xl border border-slate-200/60 overflow-x-auto">
      <table class="w-full">
        <thead class="bg-slate-50 text-xs uppercase text-bleu-nuit">
          <tr>
            <th class="text-left px-4 py-3">Projet</th>
            <th class="text-left px-4 py-3">Chef de projet</th>
            <th class="text-left px-4 py-3">Responsable Finance</th>
            <th class="text-left px-4 py-3">RÃ©gion</th>
            <th class="text-right px-4 py-3">Budget</th>
            <th class="text-left px-4 py-3">Statut</th>
            <th class="text-center px-4 py-3">Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="projet in projetsPage"
            :key="projet.id"
            class="border-t hover:bg-slate-50"
          >
            <td class="px-4 py-3">
              <h3 class="font-semibold text-sm text-slate-800">{{ projet.nom }}</h3>
              <p class="text-xs text-gray-500">{{ projet.code }}</p>
            </td>
            <td class="px-4 py-3 text-sm text-slate-700">{{ projet.chefProjet }}</td>
            <td class="px-4 py-3 text-sm text-slate-700">{{ projet.responsableFinance }}</td>
            <td class="px-4 py-3 text-sm text-slate-700">{{ projet.region }}</td>
            <td class="px-4 text-right text-sm font-semibold text-slate-900">{{ formatMontant(projet.budget) }} FCFA</td>
            <td class="px-4 py-3">
              <StatusBadge :statut="projet.statut">{{ projet.statut }}</StatusBadge>
            </td>
            <td class="px-4 py-3 text-center">
              <div class="flex justify-center gap-1">
                <RouterLink
                  :to="`/gerant/projets/${projet.id}`"
                  class="p-1 text-slate-500 hover:text-bleu-nuit rounded-lg transition-colors"
                  title="Voir"
                >
                  <Eye class="w-4 h-4" />
                </RouterLink>
                <button
                  @click="openProjet(projet)"
                  class="p-1 text-bleu-nuit hover:bg-bleu-nuit/10 rounded-lg transition-colors"
                  title="Modifier"
                >
                  <Pencil class="w-4 h-4" />
                </button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Pagination -->
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import {
  FolderKanban, Activity, Calendar, Wallet,
  Search, Eye, ChevronLeft, ChevronRight, Plus, Pencil
} from 'lucide-vue-next'
import { useGerantStore } from '@/modules/gerant/stores/gerantStore.js'
import BoutonPrimary from '@/components/ui/BoutonPrimary.vue'
import BoutonTertiary from '@/components/ui/BoutonTertiary.vue'

const store = useGerantStore()
const { formatMontant } = store

const search = ref('')
const filtreStatut = ref('')
const filtreRegion = ref('')
const currentPage = ref(1)
const itemsPerPage = 5

const statutsListe = computed(() =>
  [...new Set(store.projets.map(p => p.statut))]
)

const regionsListe = computed(() =>
  [...new Set(store.projets.map(p => p.region))]
)

const projetsActifs = computed(() => store.projets.length)
const projetsEnCours = computed(() =>
  store.projets.filter(p => p.statut === 'En cours').length
)
const projetsPlanifies = computed(() =>
  store.projets.filter(p => p.statut === 'PlanifiÃ©').length
)
const budgetTotal = computed(() =>
  store.projets.reduce((sum, p) => sum + (p.budget || 0), 0)
)

const filteredProjets = computed(() => {
  return store.projets.filter(p => {
    const matchesSearch = p.nom.toLowerCase().includes(search.value.toLowerCase()) ||
      p.code.toLowerCase().includes(search.value.toLowerCase()) ||
      p.chefProjet.toLowerCase().includes(search.value.toLowerCase())
    const matchesStatut = filtreStatut.value ? p.statut === filtreStatut.value : true
    const matchesRegion = filtreRegion.value ? p.region === filtreRegion.value : true
    return matchesSearch && matchesStatut && matchesRegion
  })
})

const projetsPage = computed(() => {
  return filteredProjets.value.slice(
    (currentPage.value - 1) * itemsPerPage,
    currentPage.value * itemsPerPage
  )
})

const totalPages = computed(() =>
  Math.max(1, Math.ceil(filteredProjets.value.length / itemsPerPage))
)

const startItem = computed(() =>
  filteredProjets.value.length === 0 ? 0 : (currentPage.value - 1) * itemsPerPage + 1
)

const endItem = computed(() =>
  Math.min(currentPage.value * itemsPerPage, filteredProjets.value.length)
)

const visiblePages = computed(() => {
  const total = totalPages.value
  if (total <= 5) return Array.from({ length: total }, (_, i) => i + 1)
  const current = currentPage.value
  let start = Math.max(1, current - 2)
  let end = Math.min(total, start + 4)
  if (end === total) start = Math.max(1, end - 4)
  return Array.from({ length: end - start + 1 }, (_, i) => start + i)
})

const resetFilters = () => {
  search.value = ''
  filtreStatut.value = ''
  filtreRegion.value = ''
}

const badgeClass = (statut) => {
  switch (statut) {
    case 'En cours':
      return 'bg-or/10 text-or'
    case 'PlanifiÃ©':
      return 'bg-or/10 text-bleu-nuit'
    case 'TerminÃ©':
      return 'bg-bleu-nuit/10 text-bleu-nuit'
    default:
      return 'bg-gray-100 text-gray-600'
  }
}

watch([search, filtreStatut, filtreRegion], () => {
  currentPage.value = 1
})
</script>





