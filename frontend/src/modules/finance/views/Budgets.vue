<template>
  <div class="p-6 space-y-6 bg-white min-h-screen">
    <!-- En-tête -->
    <div class="flex justify-between items-center  pb-4">
      <div>
        <h1 class="text-4xl font-bold text-or">Budgets</h1>
        <p class="text-xs text-gray-500 mt-1">
          Gestion budgétaire des projets assignés au module Finance
        </p>
      </div>
      <BoutonPrimary @click="modalBudget = true">
        <Plus class="w-5 h-5" />
        Nouveau budget
      </BoutonPrimary>
    </div>

    <!-- Cartes KPI -->
    <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
      <div class="bg-white border border-slate-200/60 rounded-xl p-4 flex justify-between">
        <div>
          <p class="text-xs font-bold uppercase text-slate-900">Budget total</p>
          <h3 class="text-xl font-bold text-bleu-nuit mt-2">{{ formatMontant(stat.budgetTotal) }} FCFA</h3>
        </div>
        <PiggyBank class="text-slate-400" :size="28" />
      </div>

      <div class="bg-white border border-slate-200/60 rounded-xl p-4 flex justify-between">
        <div>
          <p class="text-xs font-bold uppercase text-slate-900">Budget consommé</p>
          <h3 class="text-xl font-bold text-or mt-2">{{ formatMontant(stat.budgetConsomme) }} FCFA</h3>
        </div>
        <Receipt class="text-slate-400" :size="28" />
      </div>

      <div class="bg-white border border-slate-200/60 rounded-xl p-4 flex justify-between">
        <div>
          <p class="text-xs font-bold uppercase text-slate-900">Solde disponible</p>
          <h3 class="text-xl font-bold text-or mt-2">{{ formatMontant(stat.soldeDisponible) }} FCFA</h3>
        </div>
        <Banknote class="text-slate-400" :size="28" />
      </div>

      <div class="bg-white border border-slate-200/60 rounded-xl p-4 flex justify-between">
        <div>
          <p class="text-xs font-bold uppercase text-slate-900">Projets budgétisés</p>
          <h3 class="text-xl font-bold text-or mt-2">{{ stat.projetsBudgétises }}</h3>
        </div>
        <FolderKanban class="text-slate-400" :size="28" />
      </div>
    </div>

    <!-- Filtres -->
    <div class="bg-white border border-slate-200/60 rounded-xl p-4 grid md:grid-cols-4 gap-3">
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

      <select v-model="filtreProjet" class="border rounded-lg px-3 py-2 text-sm">
        <option>Tous les projets</option>
        <option v-for="p in store.projetsAssignes" :key="p.id" :value="p.nom">{{ p.nom }}</option>
      </select>

      <BoutonTertiary @click="resetFilters">
        Réinitialiser
      </BoutonTertiary>
    </div>

    <!-- Tableau -->
    <div class="bg-white rounded-xl border border-slate-200/60 overflow-x-auto">
      <table class="w-full">
        <thead class="bg-slate-50 text-xs uppercase text-bleu-nuit">
          <tr>
            <th class="text-left px-4 py-3">Projet</th>
            <th class="text-left px-4 py-3">Chef de projet</th>
            <th class="text-right px-4 py-3">Budget</th>
            <th class="text-right px-4 py-3">Consommé</th>
            <th class="text-right px-4 py-3">Solde</th>
            <th class="text-left px-4 py-3">Statut</th>
            <th class="text-center px-4 py-3">Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="budget in budgetsPage"
            :key="budget.id"
            class="border-t hover:bg-slate-50"
          >
            <td class="px-4 py-4">
              <h3 class="font-semibold text-sm text-slate-800">
                {{ budget.projet }}
              </h3>
            </td>
            <td class="px-4 py-3 text-sm text-slate-700">{{ budget.chefProjet }}</td>
            <td class="px-4 text-right text-sm font-semibold text-bleu-nuit">{{ formatMontant(budget.budgetTotal) }} FCFA</td>
            <td class="px-4 text-right text-sm font-semibold text-or">{{ formatMontant(budget.consomme) }} FCFA</td>
            <td class="px-4 text-right text-sm font-semibold text-or">{{ formatMontant(budget.solde) }} FCFA</td>
            <td class="px-4 py-3">
              <StatusBadge :statut="budget.statut">{{ budget.statut }}</StatusBadge>
            </td>
            <td class="px-4 py-3 text-center">
              <button
                @click="openBudget(budget)"
                class="p-1 text-or hover:bg-or/10 rounded-lg transition-colors"
                title="Voir le budget"
              >
                <Eye class="w-4 h-4" />
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Pagination -->
    <div class="flex items-center justify-between px-4 py-3 border-t border-slate-200">
      <p class="text-xs text-slate-500">
        Affichage de {{ startItem }}-{{ endItem }} sur {{ filteredBudgets.length }} budgets
      </p>
      <div class="flex items-center gap-2">
        <button
          :disabled="currentPage === 1"
          @click="currentPage -= 1"
          class="p-1 text-slate-600 hover:bg-slate-100 rounded disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          <ChevronLeft class="w-4 h-4" />
        </button>
        <div class="flex items-center gap-1">
          <button
            v-for="page in visiblePages"
            :key="page"
            @click="currentPage = page"
            :class="[
              'px-2.5 py-1 rounded text-sm font-medium transition-colors',
              page === currentPage
                ? 'bg-bleu-nuit text-white'
                : 'text-slate-600 hover:bg-slate-100'
            ]"
          >
            {{ page }}
          </button>
        </div>
        <button
          :disabled="currentPage === totalPages"
          @click="currentPage += 1"
          class="p-1 text-slate-600 hover:bg-slate-100 rounded disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          <ChevronRight class="w-4 h-4" />
        </button>
      </div>
    </div>

    <!-- Formulaire Nouveau budget (Modal) -->
    <BudgetFormModal
      v-if="modalBudget"
      :ouvert="modalBudget"
      :projets="store.projetsAssignes"
      :budget="budgetSelectionne"
      @fermer="modalBudget = false"
      @save="saveBudget"
    />
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import {
  PiggyBank, Receipt, Banknote, FolderKanban,
  Search, Eye, ChevronLeft, ChevronRight, Plus
} from 'lucide-vue-next'
import { useFinanceStore } from '@/modules/finance/stores/financeStore.js'
import BoutonPrimary from '@/components/ui/BoutonPrimary.vue'
import BoutonTertiary from '@/components/ui/BoutonTertiary.vue'
import StatusBadge from '@/components/ui/StatusBadge.vue'
import BudgetFormModal from '@/modules/finance/components/budgets/BudgetFormModal.vue'

const store = useFinanceStore()
const { formatMontant } = store

const stat = computed(() => store.budgetsStatistiques)

const search = ref('')
const filtreStatut = ref('')
const filtreProjet = ref('')
const currentPage = ref(1)
const itemsPerPage = 5

const statutsListe = computed(() =>
  [...new Set(store.budgets.map(p => p.statut))]
)

const budgetsPage = computed(() => {
  return filteredBudgets.value.slice(
    (currentPage.value - 1) * itemsPerPage,
    currentPage.value * itemsPerPage
  )
})

const filteredBudgets = computed(() => {
  return store.budgets.filter(b => {
    const matchesSearch = b.projet.toLowerCase().includes(search.value.toLowerCase()) ||
      b.chefProjet.toLowerCase().includes(search.value.toLowerCase())
    const matchesStatut = filtreStatut.value ? b.statut === filtreStatut.value : true
    const matchesProjet = filtreProjet.value ? b.projet === filtreProjet.value : true
    return matchesSearch && matchesStatut && matchesProjet
  })
})

const totalPages = computed(() =>
  Math.max(1, Math.ceil(filteredBudgets.value.length / itemsPerPage))
)

const startItem = computed(() =>
  filteredBudgets.value.length === 0 ? 0 : (currentPage.value - 1) * itemsPerPage + 1
)

const endItem = computed(() =>
  Math.min(currentPage.value * itemsPerPage, filteredBudgets.value.length)
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

const modalBudget = ref(false)
const budgetSelectionne = ref(null)

const resetFilters = () => {
  search.value = ''
  filtreStatut.value = ''
  filtreProjet.value = ''
}

const openBudget = (budget) => {
  budgetSelectionne.value = { ...budget }
  modalBudget.value = true
}

const saveBudget = (budgetData) => {
  console.log('Budget saved:', budgetData)
  modalBudget.value = false
  budgetSelectionne.value = null
}

watch([search, filtreStatut, filtreProjet], () => {
  currentPage.value = 1
})
</script>
