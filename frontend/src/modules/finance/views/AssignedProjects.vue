<template>
  <div class="p-6 space-y-6 bg-white min-h-screen">
    <!-- En-tête -->
    <div class="flex justify-between items-center border-b border-slate-200 pb-4">
      <div>
        <h1 class="text-4xl font-bold text-amber-800">Projets assignés</h1>
        <p class="text-xs text-gray-500 mt-1">
          Vue détaillée des projets alloués au module Finance
        </p>
      </div>
      <span class="text-xs text-slate-500 bg-gray-100 px-3 py-1 rounded-full">{{ totalProjets }} projet(s)</span>
    </div>

    <!-- KPI Cards -->
    <section class="grid grid-cols-1 md:grid-cols-4 gap-4">
      <div class="bg-white border border-slate-200/60 rounded-xl p-4 flex justify-between">
        <div>
          <p class="text-xs font-bold uppercase text-slate-900">Total projets</p>
          <h3 class="text-xl font-bold text-slate-900 mt-2">{{ totalProjets }}</h3>
        </div>
        <FolderKanban class="text-slate-400" :size="28" />
      </div>

      <div class="bg-white border border-slate-200/60 rounded-xl p-4 flex justify-between">
        <div>
          <p class="text-xs font-bold uppercase text-slate-900">Budget total alloué</p>
          <h3 class="text-xl font-bold text-yellow-800 mt-2">{{ formatCurrency(totalBudget) }} FCFA</h3>
        </div>
        <PiggyBank class="text-slate-400" :size="28" />
      </div>

      <div class="bg-white border border-slate-200/60 rounded-xl p-4 flex justify-between">
        <div>
          <p class="text-xs font-bold uppercase text-slate-900">Projets en cours</p>
          <h3 class="text-xl font-bold text-blue-700 mt-2">{{ projetsEnCours }}</h3>
        </div>
        <Activity class="text-slate-400" :size="28" />
      </div>

      <div class="bg-white border border-slate-200/60 rounded-xl p-4 flex justify-between">
        <div>
          <p class="text-xs font-bold uppercase text-slate-900">À budgétiser</p>
          <h3 class="text-xl font-bold text-orange-700 mt-2">{{ projetsABudgétiser }}</h3>
        </div>
        <Receipt class="text-slate-400" :size="28" />
      </div>
    </section>

    <!-- Filters -->
    <ProjectFilters
      v-model:search="searchQuery"
      v-model:statut="selectedStatut"
      v-model:chef="selectedChef"
      :statuts="statutsDisponibles"
      :chefs="chefsDisponibles"
      @reset="resetFilters"
    />

    <!-- Projects Table -->
    <ProjectsTable
      :projects="paginatedProjects"
      :current-page="currentPage"
      :items-per-page="itemsPerPage"
      :total-items="filteredProjects.length"
      @page-change="currentPage = $event"
      @open-project="openProject"
    />
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { FolderKanban, PiggyBank, Activity, Receipt } from 'lucide-vue-next'
import { projetsAssignesMock } from '../services/financeService'
import ProjectFilters from '../components/projets/ProjectFilters.vue'
import ProjectsTable from '../components/projets/ProjectsTable.vue'

const searchQuery = ref('')
const selectedStatut = ref('')
const selectedChef = ref('')
const currentPage = ref(1)
const itemsPerPage = 5

const chefsDisponibles = computed(() =>
  [...new Set(projetsAssignesMock.value.map(p => p.chefProjet))].sort()
)
const statutsDisponibles = computed(() =>
  [...new Set(projetsAssignesMock.value.map(p => p.statut))]
)

const filteredProjects = computed(() => {
  return projetsAssignesMock.value.filter(p => {
    const matchesSearch = p.nom.toLowerCase().includes(searchQuery.value.toLowerCase()) ||
      p.chefProjet.toLowerCase().includes(searchQuery.value.toLowerCase()) ||
      p.code.toLowerCase().includes(searchQuery.value.toLowerCase())
    const matchesStatut = selectedStatut.value ? p.statut === selectedStatut.value : true
    const matchesChef = selectedChef.value ? p.chefProjet === selectedChef.value : true
    return matchesSearch && matchesStatut && matchesChef
  })
})

const totalProjets = computed(() => projetsAssignesMock.value.length)

const totalBudget = computed(() =>
  projetsAssignesMock.value.reduce((sum, p) => sum + p.budget, 0)
)

const projetsEnCours = computed(() =>
  projetsAssignesMock.value.filter(p => p.statut === 'En cours').length
)

const projetsABudgétiser = computed(() =>
  projetsAssignesMock.value.filter(p => p.statut === 'À budgétiser').length
)

const paginatedProjects = computed(() => {
  const start = (currentPage.value - 1) * itemsPerPage
  const end = start + itemsPerPage
  return filteredProjects.value.slice(start, end)
})

const resetFilters = () => {
  searchQuery.value = ''
  selectedStatut.value = ''
  selectedChef.value = ''
}

const openProject = (project) => {
  console.log('Opening project:', project.nom)
}

const formatCurrency = (value) =>
  new Intl.NumberFormat('fr-FR').format(value)

watch([searchQuery, selectedStatut, selectedChef], () => {
  currentPage.value = 1
})
</script>
