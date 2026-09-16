<template>
  <div class="p-6 space-y-6 bg-white min-h-screen">
    <!-- En-tête -->
    <div class="flex justify-between items-center  pb-4">
      <div>
        <h1 class="text-4xl font-bold text-or">Partenaires</h1>
        <p class="text-xs text-gray-500 mt-1">
          Gérez les organisations partenaires des missions humanitaires.
        </p>
      </div>
      <BoutonPrimary @click="partenaireSelectionne = null; modalPartenaire = true">
        <Plus class="w-5 h-5" />
        Nouveau partenaire
      </BoutonPrimary>
    </div>

    <!-- KPI Cards -->
    <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
      <div class="bg-white border border-slate-200/60 shadow-xs rounded-xl p-4 flex justify-between">
        <div>
          <p class="text-xs font-bold uppercase text-slate-900">Total partenaires</p>
          <h3 class="text-xl font-bold text-or mt-2">{{ partenaires.length }}</h3>
        </div>
        <Handshake class="text-bleu-nuit" :size="28" />
      </div>

      <div class="bg-white border border-slate-200/60 shadow-xs rounded-xl p-4 flex justify-between">
        <div>
          <p class="text-xs font-bold uppercase text-slate-900">Partenaires actifs</p>
          <h3 class="text-xl font-bold text-or mt-2">{{ partenairesActifs }}</h3>
        </div>
        <CheckCircle class="text-bleu-nuit" :size="28" />
      </div>

      <div class="bg-white border border-slate-200/60 shadow-xs rounded-xl p-4 flex justify-between">
        <div>
          <p class="text-xs font-bold uppercase text-slate-900">Zones couvertes</p>
          <h3 class="text-xl font-bold text-or mt-2">{{ zonesCouvrir }}</h3>
        </div>
        <MapPinned class="text-bleu-nuit" :size="28" />
      </div>

      <div class="bg-white border border-slate-200/60 shadow-xs rounded-xl p-4 flex justify-between">
        <div>
          <p class="text-xs font-bold uppercase text-slate-900">Domaines d'intervention</p>
          <h3 class="text-xl font-bold text-or mt-2">{{ domainesCount }}</h3>
        </div>
        <FolderKanban class="text-bleu-nuit" :size="28" />
      </div>
    </div>

    <!-- Filtres -->
    <div class="bg-white border border-slate-200/60 shadow-xs rounded-xl p-4 grid md:grid-cols-4 gap-3">
      <div class="relative">
        <Search class="absolute left-3 top-3 text-slate-400" :size="16" />
        <input
          v-model="search"
          type="text"
          placeholder="Rechercher un partenaire..."
          class="w-full border rounded-lg pl-9 pr-3 py-2 text-sm"
        />
      </div>

      <select v-model="filtreStatut" class="border rounded-lg px-3 py-2 text-sm">
        <option>Tous les statuts</option>
        <option>ACTIF</option>
        <option>INACTIF</option>
      </select>

      <select v-model="filtreDomaine" class="border rounded-lg px-3 py-2 text-sm">
        <option>Tous les domaines</option>
        <option v-for="d in domainesListe" :key="d" :value="d">{{ d }}</option>
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
            <th class="text-left px-4 py-3">DOMAINE</th>
            <th class="text-left px-4 py-3">ZONE</th>
            <th class="text-left px-4 py-3">PROJET</th>
            <th class="text-center px-4 py-3">STATUT</th>
            <th class="text-center px-4 py-3">ACTIONS</th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="partenaire in partenairesPage"
            :key="partenaire.id"
            class="border-t hover:bg-slate-50"
          >
            <td class="px-4 py-3">
              <p class="text-slate-900 text-sm font-semibold">{{ partenaire.nom }}</p>
            </td>
            <td class="px-4 py-3 text-sm text-slate-700">{{ partenaire.domaine }}</td>
            <td class="px-4 py-3 text-sm text-slate-700">{{ partenaire.zone }}</td>
            <td class="px-4 py-3 text-sm text-slate-700">{{ partenaire.projet }}</td>
            <td class="px-4 text-center">
              <StatusBadge :statut="partenaire.statut">{{ partenaire.statut }}</StatusBadge>
            </td>
            <td class="px-4 py-3 text-center">
              <div class="flex justify-center gap-1">
                <button
                  @click="openPartenaire(partenaire)"
                  class="p-1 text-bleu-nuit hover:bg-bleu-nuit/10 rounded-lg transition-colors"
                  title="Modifier"
                >
                  <Pencil class="w-4 h-4" />
                </button>
                <button
                  @click="supprimerPartenaire(partenaire)"
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
        Affichage de {{ startItem }}-{{ endItem }} sur {{ filteredPartenaires.length }} partenaires
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
    <PartenaireFormModal
      v-if="modalPartenaire"
      :ouvert="modalPartenaire"
      :partenaire="partenaireSelectionne"
      @fermer="modalPartenaire = false"
      @save="savePartenaire"
    />
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import {
  Handshake, CheckCircle, MapPinned, FolderKanban,
  Search, ChevronLeft, ChevronRight, Plus, Pencil, Trash2
} from 'lucide-vue-next'
import { useGerantStore } from '@/modules/gerant/stores/gerantStore.js'
import BoutonPrimary from '@/components/ui/BoutonPrimary.vue'
import BoutonTertiary from '@/components/ui/BoutonTertiary.vue'
import PartenaireFormModal from '@/modules/gerant/components/partenaires/PartenaireFormModal.vue'

const store = useGerantStore()

const search = ref('')
const filtreStatut = ref('')
const filtreDomaine = ref('')
const currentPage = ref(1)
const itemsPerPage = 5

const partenaires = computed(() => store.partenaires)

const domainesListe = computed(() =>
  [...new Set(store.partenaires.map(p => p.domaine))]
)

const partenairesActifs = computed(() =>
  store.partenaires.filter(p => p.statut === 'ACTIF').length
)
const zonesCouvrir = computed(() =>
  [...new Set(store.partenaires.map(p => p.zone))].length
)
const domainesCount = computed(() =>
  [...new Set(store.partenaires.map(p => p.domaine))].length
)

const filteredPartenaires = computed(() => {
  return store.partenaires.filter(p => {
    const matchesSearch = p.nom.toLowerCase().includes(search.value.toLowerCase()) ||
      p.projet.toLowerCase().includes(search.value.toLowerCase())
    const matchesStatut = filtreStatut.value ? p.statut === filtreStatut.value : true
    const matchesDomaine = filtreDomaine.value ? p.domaine === filtreDomaine.value : true
    return matchesSearch && matchesStatut && matchesDomaine
  })
})

const partenairesPage = computed(() => {
  return filteredPartenaires.value.slice(
    (currentPage.value - 1) * itemsPerPage,
    currentPage.value * itemsPerPage
  )
})

const totalPages = computed(() =>
  Math.max(1, Math.ceil(filteredPartenaires.value.length / itemsPerPage))
)

const startItem = computed(() =>
  filteredPartenaires.value.length === 0 ? 0 : (currentPage.value - 1) * itemsPerPage + 1
)

const endItem = computed(() =>
  Math.min(currentPage.value * itemsPerPage, filteredPartenaires.value.length)
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

const modalPartenaire = ref(false)
const partenaireSelectionne = ref(null)

const resetFilters = () => {
  search.value = ''
  filtreStatut.value = ''
  filtreDomaine.value = ''
}

const openPartenaire = (partenaire) => {
  partenaireSelectionne.value = { ...partenaire }
  modalPartenaire.value = true
}

const savePartenaire = async (partenaireData) => {
  try {
    await store.savePartenaireApi(partenaireData, partenaireSelectionne.value?.id)
    modalPartenaire.value = false
    partenaireSelectionne.value = null
  } catch (error) {
    store.error = error.response?.data?.detail || "Impossible d'enregistrer le partenaire."
  }
}

const supprimerPartenaire = (partenaire) => {
  if (confirm(`Voulez-vous vraiment supprimer le partenaire "${partenaire.nom}" ?`)) {
    store.deletePartenaireApi(partenaire.id)
  }
}

const badgeClass = (statut) => {
  switch (statut) {
    case 'ACTIF':
      return 'bg-bleu-nuit/10 text-bleu-nuit'
    case 'INACTIF':
      return 'bg-gray-100 text-gray-600'
    default:
      return 'bg-gray-100 text-gray-600'
  }
}

watch([search, filtreStatut, filtreDomaine], () => {
  currentPage.value = 1
})
</script>






