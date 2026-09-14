<template>
  <div class="p-6 space-y-6 bg-white min-h-screen">
    <!-- En-tÃªte -->
    <div class="flex justify-between items-center  pb-4">
      <div>
        <h1 class="text-4xl font-bold text-or">Dons & Financements</h1>
        <p class="text-xs text-gray-500 mt-1">
          Enregistrement et suivi des financements reÃ§us
        </p>
      </div>
      <BoutonPrimary @click="modalDon = true">
        <Plus class="w-5 h-5" />
        Ajouter un financement
      </BoutonPrimary>
    </div>

    <!-- Cartes KPI -->
    <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
      <div class="bg-white border border-slate-200/60 shadow rounded-xl p-4 flex justify-between">
        <div>
          <p class="text-xs font-bold uppercase text-slate-900">Total financements</p>
          <h3 class="text-xl font-bold text-or mt-2">{{ formatMontant(stat.totalFinancements) }} FCFA</h3>
        </div>
        <Wallet class="text-bleu-nuit" :size="28" />
      </div>

      <div class="bg-white border border-slate-200/60 shadow rounded-xl p-4 flex justify-between">
        <div>
          <p class="text-xs font-bold uppercase text-slate-900">Nombre de bailleurs</p>
          <h3 class="text-xl font-bold text-or mt-2">{{ stat.nombreBailleurs }}</h3>
        </div>
        <Users class="text-bleu-nuit" :size="28" />
      </div>

      <div class="bg-white border border-slate-200/60 shadow rounded-xl p-4 flex justify-between">
        <div>
          <p class="text-xs font-bold uppercase text-slate-900">Financements du mois</p>
          <h3 class="text-xl font-bold text-or mt-2">{{ formatMontant(stat.financementDuMois) }} FCFA</h3>
        </div>
        <TrendingUp class="text-bleu-nuit" :size="28" />
      </div>

      <div class="bg-white border border-slate-200/60 shadow rounded-xl p-4 flex justify-between">
        <div>
          <p class="text-xs font-bold uppercase text-slate-900">Projets financÃ©s</p>
          <h3 class="text-xl font-bold text-or mt-2">{{ stat.projetsFinances }}</h3>
        </div>
        <FolderKanban class="text-bleu-nuit" :size="28" />
      </div>
    </div>

    <!-- Filtres -->
    <div class="bg-white border border-slate-200/60 shadow rounded-xl p-4 grid md:grid-cols-4 gap-3">
      <div class="relative">
        <Search class="absolute left-3 top-3 text-slate-400" :size="16" />
        <input
          v-model="search"
          type="text"
          placeholder="Rechercher un bailleur ou projet..."
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
        RÃ©initialiser
      </BoutonTertiary>
    </div>

    <!-- Tableau -->
    <div class="bg-white rounded-xl border border-slate-200/60 overflow-x-auto">
      <table class="w-full">
        <thead class="bg-slate-50 text-xs uppercase text-bleu-nuit">
          <tr>
            <th class="text-left px-4 py-3">Bailleur</th>
            <th class="text-left px-4 py-3">Projet</th>
            <th class="text-right px-4 py-3">Montant</th>
            <th class="text-left px-4 py-3">Date</th>
            <th class="text-left px-4 py-3">RÃ©fÃ©rence</th>
            <th class="text-left px-4 py-3">Statut</th>
            <th class="text-center px-4 py-3">Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="don in donsPage"
            :key="don.id"
            class="border-t hover:bg-slate-50"
          >
            <td class="px-4 py-3 text-sm font-semibold text-slate-800">{{ don.bailleur }}</td>
            <td class="px-4 py-3 text-sm text-slate-700">{{ don.projet }}</td>
            <td class="px-4 text-right text-sm font-semibold text-bleu-nuit">{{ formatMontant(don.montant) }} FCFA</td>
            <td class="px-4 py-3 text-sm text-slate-600">{{ formatDate(don.date) }}</td>
            <td class="px-4 py-3 text-sm text-slate-600">{{ don.reference }}</td>
            <td class="px-4 py-3">
              <StatusBadge :statut="don.statut">{{ don.statut }}</StatusBadge>
            </td>
            <td class="px-4 py-3 text-center">
              <div class="flex justify-center gap-1">
                <button
                  @click="openDon(don)"
                  class="p-1 text-bleu-nuit hover:bg-bleu-nuit/10 rounded-lg transition-colors"
                  title="Modifier"
                >
                  <Pencil class="w-4 h-4" />
                </button>
                <button
                  @click="deleteDon(don)"
                  class="p-1 text-red-600 hover:bg-red-100 rounded-lg transition-colors"
                  title="Supprimer"
                >
                  <Trash2 class="w-4 h-4" />
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
        Affichage de {{ startItem }}-{{ endItem }} sur {{ filteredDons.length }} financements
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

    <!-- Formulaire Ajouter un financement (Modal) -->
    <DonFormModal
      v-if="modalDon"
      :ouvert="modalDon"
      :projets="store.projetsAssignes"
      :bailleurs="store.bailleurs"
      :types-financement="store.typesFinancement"
      :don="donSelectionne"
      @fermer="modalDon = false"
      @save="saveDon"
    />
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import {
  Wallet, Users, TrendingUp, FolderKanban,
  Search, Eye, ChevronLeft, ChevronRight, Plus,
  Pencil, Trash2
} from 'lucide-vue-next'
import { useFinanceStore } from '@/modules/finance/stores/financeStore.js'
import BoutonPrimary from '@/components/ui/BoutonPrimary.vue'
import BoutonTertiary from '@/components/ui/BoutonTertiary.vue'
import DonFormModal from '@/modules/finance/components/dons/DonFormModal.vue'

const store = useFinanceStore()
const { formatMontant } = store

const stat = computed(() => store.donsStatistiques)

const search = ref('')
const filtreStatut = ref('')
const filtreProjet = ref('')
const currentPage = ref(1)
const itemsPerPage = 5

const statutsListe = computed(() =>
  [...new Set(store.donsFinancements.map(d => d.statut))]
)

const donsPage = computed(() => {
  return filteredDons.value.slice(
    (currentPage.value - 1) * itemsPerPage,
    currentPage.value * itemsPerPage
  )
})

const filteredDons = computed(() => {
  return store.donsFinancements.filter(d => {
    const matchesSearch = d.bailleur.toLowerCase().includes(search.value.toLowerCase()) ||
      d.projet.toLowerCase().includes(search.value.toLowerCase()) ||
      d.reference.toLowerCase().includes(search.value.toLowerCase())
    const matchesStatut = filtreStatut.value ? d.statut === filtreStatut.value : true
    const matchesProjet = filtreProjet.value ? d.projet === filtreProjet.value : true
    return matchesSearch && matchesStatut && matchesProjet
  })
})

const totalPages = computed(() =>
  Math.max(1, Math.ceil(filteredDons.value.length / itemsPerPage))
)

const startItem = computed(() =>
  filteredDons.value.length === 0 ? 0 : (currentPage.value - 1) * itemsPerPage + 1
)

const endItem = computed(() =>
  Math.min(currentPage.value * itemsPerPage, filteredDons.value.length)
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

const modalDon = ref(false)
const donSelectionne = ref(null)

const resetFilters = () => {
  search.value = ''
  filtreStatut.value = ''
  filtreProjet.value = ''
}

const openDon = (don) => {
  donSelectionne.value = { ...don }
  modalDon.value = true
}

const deleteDon = (don) => {
  console.log('Delete don:', don)
}

const saveDon = (donData) => {
  console.log('Don saved:', donData)
  modalDon.value = false
  donSelectionne.value = null
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

watch([search, filtreStatut, filtreProjet], () => {
  currentPage.value = 1
})
</script>

