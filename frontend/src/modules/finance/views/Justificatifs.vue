<template>
  <div class="p-6 space-y-6 bg-white min-h-screen">
    <!-- En-tête -->
    <div class="flex justify-between items-center  pb-4">
      <div>
        <h1 class="text-4xl font-bold text-or">Justificatifs</h1>
        <p class="text-xs text-gray-500 mt-1">
          Gestion des justificatifs de dépenses
        </p>
      </div>
      <BoutonPrimary @click="openJustificatifModal(null)">
        <Plus class="w-5 h-5" />
        Ajouter un justificatif
      </BoutonPrimary>
    </div>

    <!-- Cartes KPI -->
    <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
      <div class="bg-white border border-slate-200/60 shadow-xs rounded-xl p-4 flex justify-between">
        <div>
          <p class="text-xs font-bold uppercase text-slate-900">Validés</p>
          <h3 class="text-xl font-bold text-or mt-2">{{ stat.valides }}</h3>
        </div>
        <FileText class="text-bleu-nuit" :size="28" />
      </div>

      <div class="bg-white border border-slate-200/60 shadow-xs rounded-xl p-4 flex justify-between">
        <div>
          <p class="text-xs font-bold uppercase text-slate-900">En attente</p>
          <h3 class="text-xl font-bold text-or mt-2">{{ stat.enAttente }}</h3>
        </div>
        <Clock class="text-bleu-nuit" :size="28" />
      </div>

      <div class="bg-white border border-slate-200/60 shadow-xs rounded-xl p-4 flex justify-between">
        <div>
          <p class="text-xs font-bold uppercase text-slate-900">Montant justifié</p>
          <h3 class="text-xl font-bold text-or mt-2">{{ formatMontant(stat.montantJustifie) }} FCFA</h3>
        </div>
        <PiggyBank class="text-bleu-nuit" :size="28" />
      </div>

      <div class="bg-white border border-slate-200/60 shadow-xs rounded-xl p-4 flex justify-between">
        <div>
          <p class="text-xs font-bold uppercase text-slate-900">Dépenses sans justificatif</p>
          <h3 class="text-xl font-bold text-or mt-2">{{ stat.depensesSansJustificatif }}</h3>
        </div>
        <AlertCircle class="text-bleu-nuit" :size="28" />
      </div>
    </div>

    <!-- Filtres -->
    <div class="bg-white border border-slate-200/60 shadow-xs rounded-xl p-4 grid md:grid-cols-4 gap-3">
      <div class="relative">
        <Search class="absolute left-3 top-3 text-slate-400" :size="16" />
        <input
          v-model="search"
          type="text"
          placeholder="Rechercher un justificatif..."
          class="w-full border rounded-lg pl-9 pr-3 py-2 text-sm"
        />
      </div>

      <select v-model="filtreStatut" class="border rounded-lg px-3 py-2 text-sm">
        <option>Tous les statuts</option>
        <option v-for="s in statutsListe" :key="s" :value="s">{{ s }}</option>
      </select>

      <select v-model="filtreType" class="border rounded-lg px-3 py-2 text-sm">
        <option>Tous les types</option>
        <option v-for="t in store.typesDocument" :key="t" :value="t">{{ t }}</option>
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
            <th class="text-left px-4 py-3">Dépense</th>
            <th class="text-left px-4 py-3">Projet</th>
            <th class="text-left px-4 py-3">Type de document</th>
            <th class="text-left px-4 py-3">Date</th>
            <th class="text-right px-4 py-3">Montant</th>
            <th class="text-left px-4 py-3">Statut</th>
            <th class="text-center px-4 py-3">Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="justificatif in justificatifsPage"
            :key="justificatif.id"
            class="border-t hover:bg-slate-50"
          >
            <td class="px-4 py-3 text-sm font-semibold text-slate-800">{{ justificatif.depense }}</td>
            <td class="px-4 py-3 text-sm text-slate-700">{{ justificatif.projet }}</td>
            <td class="px-4 py-3 text-sm text-slate-700">{{ justificatif.typeDocument }}</td>
            <td class="px-4 py-3 text-sm text-slate-600">{{ formatDate(justificatif.dateDocument) }}</td>
            <td class="px-4 text-right text-sm font-semibold text-slate-900">{{ formatMontant(justificatif.montant) }} FCFA</td>
            <td class="px-4 py-3">
              <StatusBadge :statut="justificatif.statut">{{ justificatif.statut }}</StatusBadge>
            </td>
            <td class="px-4 py-3 text-center">
              <div class="flex justify-center gap-1">
                <button
                  @click="viewDocument(justificatif)"
                  class="p-1 text-bleu-nuit hover:bg-bleu-nuit/10 rounded-lg transition-colors"
                  title="Consulter"
                >
                  <Eye class="w-4 h-4" />
                </button>
                <button
                  @click="downloadDocument(justificatif)"
                  class="p-1 text-bleu-nuit hover:bg-bleu-nuit/10 rounded-lg transition-colors"
                  title="Télécharger"
                >
                  <Download class="w-4 h-4" />
                </button>
                <button
                  @click="replaceDocument(justificatif)"
                  class="p-1 text-bleu-nuit hover:bg-bleu-nuit/10 rounded-lg transition-colors"
                  title="Remplacer"
                >
                  <Replace class="w-4 h-4" />
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
        Affichage de {{ startItem }}-{{ endItem }} sur {{ filteredJustificatifs.length }} justificatifs
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

    <!-- Formulaire Ajouter/Modifier justificatif (Modal) -->
    <JustificatifFormModal
      v-if="modalJustificatif"
      :ouvert="modalJustificatif"
      :depenses="store.depenses"
      :types-document="store.typesDocument"
      :justificatif="justificatifSelectionne"
      :depense-initiale="depenseInitiale"
      @fermer="modalJustificatif = false"
      @save="saveJustificatif"
    />
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import {
  PiggyBank, FileText, Clock, AlertCircle,
  Search, Eye, Download, Replace,
  ChevronLeft, ChevronRight, Plus
} from 'lucide-vue-next'
import { useFinanceStore } from '@/modules/finance/stores/financeStore.js'
import BoutonPrimary from '@/components/ui/BoutonPrimary.vue'
import BoutonTertiary from '@/components/ui/BoutonTertiary.vue'
import JustificatifFormModal from '@/modules/finance/components/justificatifs/JustificatifFormModal.vue'
import FinancialOrbital from '@/components/ia/FinancialOrbital.vue'

const store = useFinanceStore()
const { formatMontant } = store

const stat = computed(() => store.justificatifsStatistiques)

const search = ref('')
const filtreStatut = ref('')
const filtreType = ref('')
const currentPage = ref(1)
const itemsPerPage = 5

const statutsListe = computed(() =>
  [...new Set(store.justificatifs.map(j => j.statut))]
)

const justificatifsPage = computed(() => {
  return filteredJustificatifs.value.slice(
    (currentPage.value - 1) * itemsPerPage,
    currentPage.value * itemsPerPage
  )
})

const filteredJustificatifs = computed(() => {
  return store.justificatifs.filter(j => {
    const matchesSearch = j.depense.toLowerCase().includes(search.value.toLowerCase()) ||
      j.projet.toLowerCase().includes(search.value.toLowerCase()) ||
      j.numeroDocument.toLowerCase().includes(search.value.toLowerCase())
    const matchesStatut = filtreStatut.value ? j.statut === filtreStatut.value : true
    const matchesType = filtreType.value ? j.typeDocument === filtreType.value : true
    return matchesSearch && matchesStatut && matchesType
  })
})

const totalPages = computed(() =>
  Math.max(1, Math.ceil(filteredJustificatifs.value.length / itemsPerPage))
)

const startItem = computed(() =>
  filteredJustificatifs.value.length === 0 ? 0 : (currentPage.value - 1) * itemsPerPage + 1
)

const endItem = computed(() =>
  Math.min(currentPage.value * itemsPerPage, filteredJustificatifs.value.length)
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

const modalJustificatif = ref(false)
const justificatifSelectionne = ref(null)
const depenseInitiale = ref(null)

const resetFilters = () => {
  search.value = ''
  filtreStatut.value = ''
  filtreType.value = ''
}

const openJustificatifModal = (justificatif) => {
  justificatifSelectionne.value = justificatif ? { ...justificatif } : null
  depenseInitiale.value = null
  modalJustificatif.value = true
}

const viewDocument = (justificatif) => {
  console.log('View document:', justificatif)
}

const downloadDocument = (justificatif) => {
  console.log('Download document:', justificatif)
}

const replaceDocument = (justificatif) => {
  justificatifSelectionne.value = { ...justificatif }
  modalJustificatif.value = true
}

const saveJustificatif = async (justificatifData) => {
  try {
    await store.uploadJustification(justificatifData.depenseId, justificatifData.pieceJointe)
    modalJustificatif.value = false
    justificatifSelectionne.value = null
    depenseInitiale.value = null
  } catch (error) {
    store.error = error.response?.data?.detail || error.message
  }
}

const formatDate = (dateStr) => {
  if (!dateStr) return ''
  const d = new Date(dateStr)
  return d.toLocaleDateString('fr-FR')
}

const badgeClass = (statut) => {
  switch (statut) {
    case 'Validé':
      return 'bg-bleu-nuit/10 text-bleu-nuit'
    case 'En attente':
      return 'bg-or/10 text-or'
    case 'Rejeté':
      return 'bg-red-100 text-red-700'
    default:
      return 'bg-gray-100 text-gray-600'
  }
}

watch([search, filtreStatut, filtreType], () => {
  currentPage.value = 1
})
</script>

<FinancialOrbital />


