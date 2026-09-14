<template>
  <div class="p-6 space-y-6 bg-white min-h-screen">
    <!-- En-tÃªte -->
    <div class="flex justify-between items-center  pb-4">
      <div>
        <h1 class="text-4xl font-bold text-or">Utilisateurs</h1>
        <p class="text-xs text-gray-500 mt-1">
          GÃ©rez les utilisateurs et leurs rÃ´les dans l'organisation.
        </p>
      </div>
      <BoutonPrimary to="/gerant/utilisateurs/creer">
        <Plus class="w-5 h-5" />
        Nouvel utilisateur
      </BoutonPrimary>
    </div>

    <!-- KPI Cards -->
    <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
      <div class="bg-white border border-slate-200/60 shadow rounded-xl p-4 flex justify-between">
        <div>
          <p class="text-xs font-bold uppercase text-slate-900">Total utilisateurs</p>
          <h3 class="text-xl font-bold text-or mt-2">{{ statistiques.totalUtilisateurs }}</h3>
        </div>
        <Users class="text-bleu-nuit" :size="28" />
      </div>

      <div class="bg-white border border-slate-200/60 shadow rounded-xl p-4 flex justify-between">
        <div>
          <p class="text-xs font-bold uppercase text-slate-900">Chefs de projet</p>
          <h3 class="text-xl font-bold text-or mt-2">{{ chefsProjetCount }}</h3>
        </div>
        <UserCheck class="text-bleu-nuit" :size="28" />
      </div>

      <div class="bg-white border border-slate-200/60 shadow rounded-xl p-4 flex justify-between">
        <div>
          <p class="text-xs font-bold uppercase text-slate-900">Resp. Finance</p>
          <h3 class="text-xl font-bold text-or mt-2">{{ respFinanceCount }}</h3>
        </div>
        <Wallet class="text-bleu-nuit" :size="28" />
      </div>

      <div class="bg-white border border-slate-200/60 shadow rounded-xl p-4 flex justify-between">
        <div>
          <p class="text-xs font-bold uppercase text-slate-900">Utilisateurs actifs</p>
          <h3 class="text-xl font-bold text-or mt-2">{{ utilisateursActifs }}</h3>
        </div>
        <Activity class="text-bleu-nuit" :size="28" />
      </div>
    </div>

    <!-- Filtres -->
    <div class="bg-white border border-slate-200/60 shadow rounded-xl p-4 grid md:grid-cols-4 gap-3">
      <div class="relative">
        <Search class="absolute left-3 top-3 text-slate-400" :size="16" />
        <input
          v-model="search"
          type="text"
          placeholder="Rechercher un utilisateur..."
          class="w-full border rounded-lg pl-9 pr-3 py-2 text-sm"
        />
      </div>

      <select v-model="filtreRole" class="border rounded-lg px-3 py-2 text-sm">
        <option>Tous les rÃ´les</option>
        <option v-for="r in rolesListe" :key="r" :value="r">{{ r }}</option>
      </select>

      <select v-model="filtreStatut" class="border rounded-lg px-3 py-2 text-sm">
        <option>Tous les statuts</option>
        <option>Actif</option>
        <option>Inactif</option>
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
            <th class="text-left px-4 py-3">Nom</th>
            <th class="text-left px-4 py-3">Email</th>
            <th class="text-left px-4 py-3">RÃ´le</th>
            <th class="text-left px-4 py-3">Projet</th>
            <th class="text-left px-4 py-3">Statut</th>
            <th class="text-center px-4 py-3">Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="utilisateur in utilisateursPage"
            :key="utilisateur.id"
            class="border-t hover:bg-slate-50"
          >
            <td class="px-4 py-3">
              <h3 class="font-semibold text-sm text-slate-800">{{ utilisateur.nom }}</h3>
            </td>
            <td class="px-4 py-3 text-sm text-slate-600">{{ utilisateur.email }}</td>
            <td class="px-4 py-3 text-sm text-slate-700">{{ utilisateur.role }}</td>
            <td class="px-4 py-3 text-sm text-slate-700">{{ utilisateur.projet }}</td>
            <td class="px-4 py-3">
              <StatusBadge :statut="utilisateur.statut">{{ utilisateur.statut }}</StatusBadge>
            </td>
            <td class="px-4 py-3 text-center">
              <div class="flex justify-center gap-1">
                <button
                  @click="openUtilisateur(utilisateur)"
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
    <!-- Form Modal removed - now navigates to full page -->
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import {
  Users, UserCheck, Wallet, Activity,
  Search, Plus, Pencil
} from 'lucide-vue-next'
import { useGerantStore } from '@/modules/gerant/stores/gerantStore.js'
import BoutonPrimary from '@/components/ui/BoutonPrimary.vue'
import BoutonTertiary from '@/components/ui/BoutonTertiary.vue'

const store = useGerantStore()

const statistiques = computed(() => store.statistiques)

const search = ref('')
const filtreRole = ref('')
const filtreStatut = ref('')
const currentPage = ref(1)
const itemsPerPage = 5

const rolesListe = computed(() =>
  [...new Set(store.utilisateurs.map(u => u.role))]
)

const chefsProjetCount = computed(() =>
  store.utilisateurs.filter(u => u.role === 'Chef de projet').length
)
const respFinanceCount = computed(() =>
  store.utilisateurs.filter(u => u.role === 'Responsable Finance').length
)
const utilisateursActifs = computed(() =>
  store.utilisateurs.filter(u => u.statut === 'Actif').length
)

const filteredUtilisateurs = computed(() => {
  return store.utilisateurs.filter(u => {
    const matchesSearch = u.nom.toLowerCase().includes(search.value.toLowerCase()) ||
      u.email.toLowerCase().includes(search.value.toLowerCase())
    const matchesRole = filtreRole.value ? u.role === filtreRole.value : true
    const matchesStatut = filtreStatut.value ? u.statut === filtreStatut.value : true
    return matchesSearch && matchesRole && matchesStatut
  })
})

const utilisateursPage = computed(() => {
  return filteredUtilisateurs.value.slice(
    (currentPage.value - 1) * itemsPerPage,
    currentPage.value * itemsPerPage
  )
})

const totalPages = computed(() =>
  Math.max(1, Math.ceil(filteredUtilisateurs.value.length / itemsPerPage))
)

const startItem = computed(() =>
  filteredUtilisateurs.value.length === 0 ? 0 : (currentPage.value - 1) * itemsPerPage + 1
)

const endItem = computed(() =>
  Math.min(currentPage.value * itemsPerPage, filteredUtilisateurs.value.length)
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
  filtreRole.value = ''
  filtreStatut.value = ''
}

const badgeClass = (statut) => {
  switch (statut) {
    case 'Actif':
      return 'bg-bleu-nuit/10 text-bleu-nuit'
    case 'Inactif':
      return 'bg-gray-100 text-gray-600'
    default:
      return 'bg-gray-100 text-gray-600'
  }
}

watch([search, filtreRole, filtreStatut], () => {
  currentPage.value = 1
})
</script>





