<template>
  <div class="p-6 space-y-6 bg-white min-h-screen">
    <!-- En-tête -->
    <div class="flex justify-between items-center  pb-4">
      <div>
        <h1 class="text-4xl font-bold text-or">Bailleurs</h1>
        <p class="text-xs text-gray-500 mt-1">
          Gérez les bailleurs de fonds des missions humanitaires.
        </p>
      </div>
      <BoutonPrimary @click="bailleurSelectionne = null; modalBailleur = true">
        <Plus class="w-5 h-5" />
        Nouveau bailleur
      </BoutonPrimary>
    </div>

    <!-- KPI Cards -->
    <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
      <div class="bg-white border border-slate-200/60 shadow-xs rounded-xl p-4 flex justify-between">
        <div>
          <p class="text-xs font-bold uppercase text-slate-900">Total bailleurs</p>
          <h3 class="text-xl font-bold text-or mt-2">{{ bailleurs.length }}</h3>
        </div>
        <Landmark class="text-bleu-nuit" :size="28" />
      </div>

      <div class="bg-white border border-slate-200/60 shadow-xs rounded-xl p-4 flex justify-between">
        <div>
          <p class="text-xs font-bold uppercase text-slate-900">Financement total</p>
          <h3 class="text-xl font-bold text-or mt-2">{{ formatMontant(bailleursFinance) }} FCFA</h3>
        </div>
        <PiggyBank class="text-bleu-nuit" :size="28" />
      </div>

      <div class="bg-white border border-slate-200/60 shadow-xs rounded-xl p-4 flex justify-between">
        <div>
          <p class="text-xs font-bold uppercase text-slate-900">Reçus</p>
          <h3 class="text-xl font-bold text-or mt-2">{{ bailleursRecus }}</h3>
        </div>
        <CheckCircle class="text-bleu-nuit" :size="28" />
      </div>

      <div class="bg-white border border-slate-200/60 shadow-xs rounded-xl p-4 flex justify-between">
        <div>
          <p class="text-xs font-bold uppercase text-slate-900">En attente</p>
          <h3 class="text-xl font-bold text-or mt-2">{{ bailleursEnAttente }}</h3>
        </div>
        <Clock class="text-bleu-nuit" :size="28" />
      </div>
    </div>

    <!-- Filtres -->
    <div class="bg-white border border-slate-200/60 shadow-xs rounded-xl p-4 grid md:grid-cols-4 gap-3">
      <div class="relative">
        <Search class="absolute left-3 top-3 text-slate-400" :size="16" />
        <input
          v-model="search"
          type="text"
          placeholder="Rechercher par nom d'organisation..."
          class="w-full border rounded-lg pl-9 pr-3 py-2 text-sm"
        />
      </div>

      <select v-model="filtreStatut" class="border rounded-lg px-3 py-2 text-sm">
        <option>Tous les statuts</option>
        <option>Reçu</option>
        <option>En attente</option>
      </select>

      <select v-model="filtreType" class="border rounded-lg px-3 py-2 text-sm">
        <option>Tous les types</option>
        <option>International</option>
        <option>National</option>
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
            <th class="text-left px-4 py-3">ORGANISATION</th>
            <th class="text-left px-4 py-3">CONTACT</th>
            <th class="text-left px-4 py-3">TYPE</th>
            <th class="text-right px-4 py-3">FINANCEMENT ENGAGÉ</th>
            <th class="text-center px-4 py-3">STATUT</th>
            <th class="text-center px-4 py-3">ACTIONS</th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="bailleur in bailleursFiltresPage"
            :key="bailleur.id"
            class="border-t hover:bg-slate-50"
          >
            <td class="px-4 py-3">
              <p class="text-slate-900 text-sm font-semibold">{{ bailleur.nom }}</p>
            </td>
            <td class="px-4 py-3 text-sm text-slate-600">{{ bailleur.contact }}</td>
            <td class="px-4 py-3 text-sm text-slate-700">{{ bailleur.type }}</td>
            <td class="px-4 text-right text-sm font-semibold text-slate-900">{{ formatMontant(bailleurFinances[bailleur.id]) }} FCFA</td>
            <td class="px-4 text-center">
              <StatusBadge :statut="bailleur.statut">{{ bailleur.statut }}</StatusBadge>
            </td>
            <td class="px-4 py-3 text-center">
              <div class="flex justify-center gap-1">
                <button
                  @click="openBailleur(bailleur)"
                  class="p-1 text-bleu-nuit hover:bg-bleu-nuit/10 rounded-lg transition-colors"
                  title="Modifier"
                >
                  <Pencil class="w-4 h-4" />
                </button>
                <button
                  @click="supprimerBailleur(bailleur)"
                  class="p-1 text-slate-400 hover:text-red-600 rounded-lg transition-colors"
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
        Affichage de {{ startItem }}-{{ endItem }} sur {{ filteredBailleurs.length }} bailleurs
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

    <!-- Formulaire (Modal) -->
    <BailleurFormModal
      v-if="modalBailleur"
      :ouvert="modalBailleur"
      :bailleur="bailleurSelectionne"
      @fermer="modalBailleur = false"
      @save="saveBailleur"
    />
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import {
  Landmark, PiggyBank, CheckCircle, Clock,
  Search, ChevronLeft, ChevronRight, Plus, Pencil, Trash2
} from 'lucide-vue-next'
import { useGerantStore } from '@/modules/gerant/stores/gerantStore.js'
import BoutonPrimary from '@/components/ui/BoutonPrimary.vue'
import BoutonTertiary from '@/components/ui/BoutonTertiary.vue'
import BailleurFormModal from '@/modules/gerant/components/bailleurs/BailleurFormModal.vue'
import ExecutiveOrbitalIA from '@/components/ia/ExecutiveOrbitalIA.vue'

const store = useGerantStore()
const { formatMontant } = store

const search = ref('')
const filtreStatut = ref('')
const filtreType = ref('')
const currentPage = ref(1)
const itemsPerPage = 5

const bailleurs = computed(() => store.bailleurs)

const parseEuro = (val) => {
  if (typeof val === 'number') return val
  if (!val) return 0
  const str = String(val)
  const clean = str.replace(/[^\d.,]/g, '').replace(',', '.')
  const num = parseFloat(clean) || 0
  if (str.includes('€') || str.toLowerCase().includes('eur')) {
    return Math.round(num * 650)
  }
  return Math.round(num)
}

const bailleursFinance = computed(() => {
  return store.bailleurs.reduce((sum, b) => sum + parseEuro(b.finance), 0)
})

const bailleursRecus = computed(() =>
  store.bailleurs.filter(b => b.statut === 'Reçu' || b.statut === 'Reçu').length
)
const bailleursEnAttente = computed(() =>
  store.bailleurs.filter(b => b.statut === 'En attente').length
)

const bailleurFinances = computed(() => {
  const map = {}
  store.bailleurs.forEach(b => {
    map[b.id] = parseEuro(b.finance)
  })
  return map
})

const filteredBailleurs = computed(() => {
  return store.bailleurs.filter(b => {
    const matchesSearch = b.nom.toLowerCase().includes(search.value.toLowerCase()) ||
      b.contact.toLowerCase().includes(search.value.toLowerCase())
    const matchesStatut = filtreStatut.value ? b.statut === filtreStatut.value : true
    const matchesType = filtreType.value ? b.type === filtreType.value : true
    return matchesSearch && matchesStatut && matchesType
  })
})

const bailleursFiltresPage = computed(() => {
  return filteredBailleurs.value.slice(
    (currentPage.value - 1) * itemsPerPage,
    currentPage.value * itemsPerPage
  )
})

const totalPages = computed(() =>
  Math.max(1, Math.ceil(filteredBailleurs.value.length / itemsPerPage))
)

const startItem = computed(() =>
  filteredBailleurs.value.length === 0 ? 0 : (currentPage.value - 1) * itemsPerPage + 1
)

const endItem = computed(() =>
  Math.min(currentPage.value * itemsPerPage, filteredBailleurs.value.length)
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

const modalBailleur = ref(false)
const bailleurSelectionne = ref(null)

const resetFilters = () => {
  search.value = ''
  filtreStatut.value = ''
  filtreType.value = ''
}

const openBailleur = (bailleur) => {
  bailleurSelectionne.value = { ...bailleur }
  modalBailleur.value = true
}

const saveBailleur = async (bailleurData) => {
  try {
    await store.saveBailleurApi(bailleurData, bailleurSelectionne.value?.id)
    modalBailleur.value = false
    bailleurSelectionne.value = null
  } catch (error) {
    store.error = error.response?.data?.detail || "Impossible d'enregistrer le bailleur."
  }
}

const supprimerBailleur = (bailleur) => {
  if (confirm(`Voulez-vous vraiment supprimer le bailleur "${bailleur.nom}" ?`)) {
    store.deleteBailleurApi(bailleur.id)
  }
}

const badgeClass = (statut) => {
  switch (statut) {
    case 'Reçu':
      return 'bg-bleu-nuit/10 text-bleu-nuit'
    case 'En attente':
      return 'bg-or/10 text-or'
    default:
      return 'bg-gray-100 text-gray-600'
  }
}

watch([search, filtreStatut, filtreType], () => {
  currentPage.value = 1
})
</script>

<ExecutiveOrbitalIA />






