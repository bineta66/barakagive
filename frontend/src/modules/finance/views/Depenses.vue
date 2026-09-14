<template>
  <div class="p-6 space-y-6 bg-white min-h-screen">
    <!-- En-tÃªte -->
    <div class="flex justify-between items-center  pb-4">
      <div>
        <h1 class="text-4xl font-bold text-or">DÃ©penses</h1>
        <p class="text-xs text-gray-500 mt-1">
          Enregistrement et suivi des dÃ©penses par projet
        </p>
      </div>
      <BoutonPrimary @click="openDepenseModal(null)">
        <Plus class="w-5 h-5" />
        Nouvelle dÃ©pense
      </BoutonPrimary>
    </div>

    <!-- Cartes KPI -->
    <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
      <div class="bg-white border border-slate-200/60 shadow rounded-xl p-4 flex justify-between">
        <div>
          <p class="text-xs font-bold uppercase text-slate-900">DÃ©penses totales</p>
          <h3 class="text-xl font-bold text-or mt-2">{{ formatMontant(stat.depensesTotales) }} FCFA</h3>
        </div>
        <Wallet class="text-bleu-nuit" :size="28" />
      </div>

      <div class="bg-white border border-slate-200/60 shadow rounded-xl p-4 flex justify-between">
        <div>
          <p class="text-xs font-bold uppercase text-slate-900">DÃ©penses du mois</p>
          <h3 class="text-xl font-bold text-or mt-2">{{ formatMontant(stat.depensesDuMois) }} FCFA</h3>
        </div>
        <Receipt class="text-bleu-nuit" :size="28" />
      </div>

      <div class="bg-white border border-slate-200/60 shadow rounded-xl p-4 flex justify-between">
        <div>
          <p class="text-xs font-bold uppercase text-slate-900">Nombre d'opÃ©rations</p>
          <h3 class="text-xl font-bold text-or mt-2">{{ stat.nombreOperations }}</h3>
        </div>
        <Activity class="text-bleu-nuit" :size="28" />
      </div>

      <div class="bg-white border border-slate-200/60 shadow rounded-xl p-4 flex justify-between">
        <div>
          <p class="text-xs font-bold uppercase text-slate-900">Budget restant</p>
          <h3 class="text-xl font-bold text-or mt-2">{{ formatMontant(stat.budgetRestant) }} FCFA</h3>
        </div>
        <Banknote class="text-bleu-nuit" :size="28" />
      </div>
    </div>

    <!-- Filtres -->
    <div class="bg-white border border-slate-200/60 shadow rounded-xl p-4 grid md:grid-cols-4 gap-3">
      <div class="relative">
        <Search class="absolute left-3 top-3 text-slate-400" :size="16" />
        <input
          v-model="search"
          type="text"
          placeholder="Rechercher une dÃ©pense..."
          class="w-full border rounded-lg pl-9 pr-3 py-2 text-sm"
        />
      </div>

      <select v-model="filtreCategorie" class="border rounded-lg px-3 py-2 text-sm">
        <option>Toutes les catÃ©gories</option>
        <option v-for="c in store.categoriesDepense" :key="c" :value="c">{{ c }}</option>
      </select>

      <select v-model="filtreProjet" class="border rounded-lg px-3 py-2 text-sm">
        <option>Tous les projets</option>
        <option v-for="p in store.projetsAssignes" :key="p.id" :value="p.nom">{{ p.nom }}</option>
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
            <th class="text-left px-4 py-3">Date</th>
            <th class="text-left px-4 py-3">Projet</th>
            <th class="text-left px-4 py-3">CatÃ©gorie</th>
            <th class="text-right px-4 py-3">Montant</th>
            <th class="text-left px-4 py-3">Statut</th>
            <th class="text-center px-4 py-3">Justificatif</th>
            <th class="text-center px-4 py-3">Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="depense in depensesPage"
            :key="depense.id"
            class="border-t hover:bg-slate-50"
          >
            <td class="px-4 py-3 text-sm text-slate-600">{{ formatDate(depense.date) }}</td>
            <td class="px-4 py-3 text-sm text-slate-700">{{ depense.projet }}</td>
            <td class="px-4 py-3 text-sm text-slate-700">{{ depense.categorie }}</td>
            <td class="px-4 text-right text-sm font-semibold text-red-700">{{ formatMontant(depense.montant) }} FCFA</td>
            <td class="px-4 py-3">
              <StatusBadge :statut="depense.statut">{{ depense.statut }}</StatusBadge>
            </td>
            <td class="px-4 py-3 text-center">
              <span
                v-if="depense.justificatif"
                class="text-xs text-emerald-600 font-medium"
              >
                AttachÃ©
              </span>
              <span
                v-else
                class="text-xs text-red-500 font-medium"
              >
                Manquant
              </span>
            </td>
            <td class="px-4 py-3 text-center">
              <div class="flex justify-center gap-1">
                <button
                  @click="openDepenseModal(depense)"
                  class="p-1 text-bleu-nuit hover:bg-bleu-nuit/10 rounded-lg transition-colors"
                  title="Modifier"
                >
                  <Pencil class="w-4 h-4" />
                </button>
                <button
                  @click="addJustificatif(depense)"
                  class="p-1 text-bleu-nuit hover:bg-bleu-nuit/10 rounded-lg transition-colors"
                  title="Ajouter justificatif"
                >
                  <FileText class="w-4 h-4" />
                </button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Pagination -->
    <div class="flex items-center justify-between px-4 py-3 border-t border-slate-200">
      <p class="text-xs text-slate-500">
        Affichage de {{ startItem }}-{{ endItem }} sur {{ filteredDepenses.length }} dÃ©penses
      </p>
      <div class="flex items-center gap-2">
        <button
          :disabled="currentPage === 1"
          @click="currentPage -= 1"
          class="p-1 text-bleu-nuit hover:bg-bleu-nuit/10 rounded disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
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
                ? 'bg-or text-white'
                : 'text-bleu-nuit hover:bg-bleu-nuit/10'
            ]"
          >
            {{ page }}
          </button>
        </div>
        <button
          :disabled="currentPage === totalPages"
          @click="currentPage += 1"
          class="p-1 text-bleu-nuit hover:bg-bleu-nuit/10 rounded disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          <ChevronRight class="w-4 h-4" />
        </button>
      </div>
    </div>

    <!-- Formulaire Nouvelle dÃ©pense (Modal) -->
    <DepenseFormModal
      v-if="modalDepense"
      :ouvert="modalDepense"
      :projets="store.projetsAssignes"
      :categories="store.categoriesDepense"
      :modes-paiement="store.modesPaiement"
      :depense="depenseSelectionne"
      @fermer="modalDepense = false"
      @save="saveDepense"
    />

    <!-- Formulaire Ajouter justificatif (Modal) -->
    <JustificatifFormModal
      v-if="modalJustificatif"
      :ouvert="modalJustificatif"
      :depenses="store.depenses"
      :types-document="store.typesDocument"
      :depense-initiale="depenseJustificatifSelectionnee"
      @fermer="modalJustificatif = false"
      @save="saveJustificatif"
    />
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import {
  Wallet, Receipt, Activity, Banknote, FolderKanban,
  Search, ChevronLeft, ChevronRight, Plus,
  Pencil, FileText
} from 'lucide-vue-next'
import { useFinanceStore } from '@/modules/finance/stores/financeStore.js'
import BoutonPrimary from '@/components/ui/BoutonPrimary.vue'
import BoutonTertiary from '@/components/ui/BoutonTertiary.vue'
import DepenseFormModal from '@/modules/finance/components/depenses/DepenseFormModal.vue'
import JustificatifFormModal from '@/modules/finance/components/justificatifs/JustificatifFormModal.vue'

const store = useFinanceStore()
const { formatMontant } = store

const stat = computed(() => store.depensesStatistiques)

const search = ref('')
const filtreCategorie = ref('')
const filtreProjet = ref('')
const currentPage = ref(1)
const itemsPerPage = 5

const depensesPage = computed(() => {
  return filteredDepenses.value.slice(
    (currentPage.value - 1) * itemsPerPage,
    currentPage.value * itemsPerPage
  )
})

const filteredDepenses = computed(() => {
  return store.depenses.filter(d => {
    const matchesSearch = d.libelle.toLowerCase().includes(search.value.toLowerCase()) ||
      d.projet.toLowerCase().includes(search.value.toLowerCase()) ||
      d.categorie.toLowerCase().includes(search.value.toLowerCase()) ||
      d.fournisseur.toLowerCase().includes(search.value.toLowerCase())
    const matchesCategorie = filtreCategorie.value ? d.categorie === filtreCategorie.value : true
    const matchesProjet = filtreProjet.value ? d.projet === filtreProjet.value : true
    return matchesSearch && matchesCategorie && matchesProjet
  })
})

const totalPages = computed(() =>
  Math.max(1, Math.ceil(filteredDepenses.value.length / itemsPerPage))
)

const startItem = computed(() =>
  filteredDepenses.value.length === 0 ? 0 : (currentPage.value - 1) * itemsPerPage + 1
)

const endItem = computed(() =>
  Math.min(currentPage.value * itemsPerPage, filteredDepenses.value.length)
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

const modalDepense = ref(false)
const depenseSelectionne = ref(null)
const modalJustificatif = ref(false)
const depenseJustificatifSelectionnee = ref(null)

const resetFilters = () => {
  search.value = ''
  filtreCategorie.value = ''
  filtreProjet.value = ''
}

const openDepenseModal = (depense) => {
  depenseSelectionne.value = depense ? { ...depense } : null
  modalDepense.value = true
}

const saveDepense = (depenseData) => {
  if (!depenseData.id) {
    const newId = Math.max(...store.depenses.map(d => d.id), 0) + 1
    depenseData.id = newId
    store.depenses.push(depenseData)
  } else {
    const idx = store.depenses.findIndex(d => d.id === depenseData.id)
    if (idx !== -1) store.depenses[idx] = depenseData
  }
  modalDepense.value = false
  depenseSelectionne.value = null

  depenseJustificatifSelectionnee.value = { id: depenseData.id, projet: depenseData.projet }
  modalJustificatif.value = true
}

const addJustificatif = (depense) => {
  depenseJustificatifSelectionnee.value = { id: depense.id, projet: depense.projet }
  modalJustificatif.value = true
}

const saveJustificatif = (justificatifData) => {
  const newId = Math.max(...store.justificatifs.map(j => j.id), 0) + 1
  const depense = store.depenses.find(d => d.id === justificatifData.depenseId)
  if (depense) depense.justificatif = newId

  const newJustificatif = {
    ...justificatifData,
    id: newId,
  }
  store.justificatifs.push(newJustificatif)

  modalJustificatif.value = false
  depenseJustificatifSelectionnee.value = null
}

const formatDate = (dateStr) => {
  if (!dateStr) return ''
  const d = new Date(dateStr)
  return d.toLocaleDateString('fr-FR')
}

const badgeClass = (statut) => {
  switch (statut) {
    case 'ValidÃ©':
      return 'bg-bleu-nuit/10 text-bleu-nuit'
    case 'En attente':
      return 'bg-or/10 text-or'
    case 'RejetÃ©':
      return 'bg-red-100 text-red-700'
    default:
      return 'bg-gray-100 text-gray-600'
  }
}

watch([search, filtreCategorie, filtreProjet], () => {
  currentPage.value = 1
})
</script>

