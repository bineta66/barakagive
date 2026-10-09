<template>
  <div class="p-6 space-y-6 bg-white min-h-screen">
    <!-- Titre et Action -->
    <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 pb-4 border-b border-slate-100">
      <div>
        <h1 class="text-4xl font-bold text-bleu-nuit">Mes projets</h1>
        <p class="text-xs text-gray-500 mt-1">
          Gérez, suivez et mettez à jour les projets humanitaires sur le terrain.
        </p>
      </div>

      <BoutonPrimary v-if="peutGererProjets" @click="openCreateModal">
        <Plus :size="18" />
        Nouveau projet
      </BoutonPrimary>
    </div>

    <!-- Alert and Loading -->
    <LoadingSpinner v-if="projectStore.loading && !projectStore.projects.length" message="Chargement des projets..." />
    <AlertMessage v-if="feedback.message" :type="feedback.type" :message="feedback.message" class="mb-4" />

    <!-- Cartes statistiques -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
      <div class="bg-white border border-slate-200/60 shadow-xs rounded-xl p-4 flex justify-between">
        <div>
          <p class="text-xs font-bold uppercase text-slate-500">Volume budgétaire alloué</p>
          <h3 class="text-xl font-bold text-bleu-nuit mt-1">{{ formatBudget(totalBudget) }}</h3>
        </div>
        <Wallet class="text-bleu-nuit" :size="28" />
      </div>

      <div class="bg-white border border-slate-200/60 shadow-xs rounded-xl p-4 flex justify-between">
        <div>
          <p class="text-xs font-bold uppercase text-slate-500">Projets actifs</p>
          <h3 class="text-xl font-bold text-bleu-nuit mt-1">{{ activeProjectsCount }}</h3>
        </div>
        <Activity class="text-bleu-nuit" :size="28" />
      </div>

      <div class="bg-white border border-slate-200/60 shadow-xs rounded-xl p-4 flex justify-between">
        <div>
          <p class="text-xs font-bold uppercase text-slate-500">Total projets</p>
          <h3 class="text-xl font-bold text-slate-800 mt-1">{{ projectStore.projects.length }}</h3>
        </div>
        <FolderKanban class="text-bleu-nuit" :size="28" />
      </div>
    </div>

    <!-- Filtres -->
    <div class="bg-white border border-slate-200/60 shadow-xs rounded-xl p-4 grid md:grid-cols-3 gap-3">
      <select v-model="filtreStatut" class="border border-slate-200 rounded-lg px-3 py-2 text-sm bg-white focus:outline-none focus:ring-2 focus:ring-bleu-nuit/30">
        <option value="Tous les statuts">Tous les statuts</option>
        <option value="Actif">Actifs</option>
        <option value="Archivé">Archivés</option>
      </select>

      <select v-model="filtreRegion" class="border border-slate-200 rounded-lg px-3 py-2 text-sm bg-white focus:outline-none focus:ring-2 focus:ring-bleu-nuit/30">
        <option value="Toutes les régions">Toutes les régions</option>
        <option v-for="reg in regionsList" :key="reg" :value="reg">{{ reg }}</option>
      </select>

      <div class="relative">
        <Search class="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" :size="16" />
        <input
          v-model="recherche"
          type="text"
          placeholder="Rechercher par nom ou code..."
          class="w-full border border-slate-200 rounded-lg pl-9 pr-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-bleu-nuit/30"
        />
      </div>
    </div>

    <div class="flex justify-end gap-2">
      <button type="button" @click="modeAffichage = 'cartes'" :aria-pressed="modeAffichage === 'cartes'" class="inline-flex items-center gap-2 rounded-lg border px-3 py-2 text-sm font-semibold transition" :class="modeAffichage === 'cartes' ? 'border-bleu-nuit bg-bleu-nuit text-white' : 'border-slate-200 bg-white text-slate-600 hover:bg-slate-50'"><LayoutGrid :size="16" />Cartes</button>
      <button type="button" @click="modeAffichage = 'tableau'" :aria-pressed="modeAffichage === 'tableau'" class="inline-flex items-center gap-2 rounded-lg border px-3 py-2 text-sm font-semibold transition" :class="modeAffichage === 'tableau' ? 'border-bleu-nuit bg-bleu-nuit text-white' : 'border-slate-200 bg-white text-slate-600 hover:bg-slate-50'"><List :size="16" />Tableau</button>
    </div>

    <div v-if="modeAffichage === 'tableau'" class="overflow-x-auto rounded-xl border border-slate-200/60 bg-white">
      <table class="w-full min-w-[760px] text-left text-sm">
        <thead class="bg-slate-50 text-xs uppercase tracking-wide text-bleu-nuit">
          <tr><th class="px-4 py-4">Projet</th><th class="px-4 py-4">Région</th><th class="px-4 py-4">Budget</th><th class="px-4 py-4">Dates</th><th class="px-4 py-4">Statut</th><th class="px-4 py-4 text-right">Actions</th></tr>
        </thead>
        <tbody class="divide-y divide-slate-100">
          <tr v-for="projet in projetsPage" :key="projet.id" class="hover:bg-slate-50/70">
            <td class="px-4 py-4"><p class="font-semibold text-slate-800">{{ projet.name || projet.nom }}</p><p class="mt-0.5 text-xs text-slate-500">{{ projet.code || 'Sans code' }}</p></td>
            <td class="px-4 py-4 text-slate-600">{{ projet.region || 'Non renseignée' }}</td>
            <td class="px-4 py-4 font-medium text-slate-700">{{ formatBudget(projet.budget) }}</td>
            <td class="px-4 py-4 text-slate-600">{{ projet.start_date || '-' }} – {{ projet.end_date || '-' }}</td>
            <td class="px-4 py-4"><span class="rounded-full px-2.5 py-1 text-xs font-semibold" :class="projet.archived ? 'bg-slate-100 text-slate-600' : 'bg-emerald-50 text-emerald-700'">{{ projet.archived ? 'Archivé' : 'Actif' }}</span></td>
            <td class="px-4 py-4"><div class="flex justify-end gap-2">
              <RouterLink :to="{ name: 'projets-detail', params: { id: projet.id || projet.code } }" class="rounded-lg p-2 text-slate-500 hover:bg-slate-100 hover:text-bleu-nuit" title="Détails" aria-label="Détails"><Eye :size="16" /></RouterLink>
              <button v-if="peutGererProjets && !projet.archived" class="rounded-lg px-3 py-2 text-xs font-semibold text-bleu-nuit hover:bg-slate-100" @click="openEditProject(projet)">Modifier</button>
              <button v-if="peutGererProjets && !projet.archived" class="rounded-lg px-3 py-2 text-xs font-semibold text-red-600 hover:bg-red-50" @click="handleDeleteProject(projet.id)">Archiver</button>
            </div></td>
          </tr>
          <tr v-if="!projetsPage.length"><td colspan="6" class="px-4 py-10 text-center text-slate-500">Aucun projet ne correspond aux filtres.</td></tr>
        </tbody>
      </table>
    </div>

    <div v-else-if="projetsPage.length" class="grid grid-cols-1 gap-4 lg:grid-cols-2">
      <article v-for="projet in projetsPage" :key="projet.id" class="overflow-hidden rounded-xl border border-slate-200/70 bg-white/75 text-slate-800 backdrop-blur-xl">
        <div class="border-b border-slate-200/70 p-5">
          <div class="flex items-start justify-between gap-3">
            <div class="min-w-0"><h2 class="truncate text-lg font-bold text-slate-900">{{ projet.name || projet.nom }}</h2><p class="mt-1 text-xs text-slate-500">{{ projet.code || 'Sans code' }}</p></div>
            <span class="shrink-0 rounded-full px-2.5 py-1 text-xs font-semibold" :class="projet.archived ? 'bg-slate-100 text-slate-600' : 'bg-emerald-50 text-emerald-700'">{{ projet.archived ? 'Archive' : 'Actif' }}</span>
          </div>
          <p class="mt-3 line-clamp-2 min-h-10 text-sm text-slate-600">{{ projet.description || projet.objectif || 'Aucune description disponible.' }}</p>
          <div class="mt-4 grid grid-cols-2 gap-3 text-xs">
            <div class="rounded-lg border border-slate-200/70 bg-slate-100/70 p-3"><p class="text-slate-500">Région</p><span class="mt-1 inline-flex items-center rounded-full border border-slate-300 bg-slate-100 px-2.5 py-1 font-semibold text-bleu-nuit">{{ projet.region || 'Non renseignée' }}</span></div>
            <div class="rounded-lg border border-slate-200/70 bg-slate-100/70 p-3"><p class="text-slate-500">Budget</p><p class="mt-1 font-semibold text-slate-800">{{ formatBudget(projet.budget) }}</p></div>
            <div class="rounded-lg border border-slate-200/70 bg-slate-100/70 p-3"><p class="text-slate-500">Début</p><p class="mt-1 font-semibold text-slate-800">{{ projet.start_date || '-' }}</p></div>
            <div class="rounded-lg border border-slate-200/70 bg-slate-100/70 p-3"><p class="text-slate-500">Fin</p><p class="mt-1 font-semibold text-slate-800">{{ projet.end_date || '-' }}</p></div>
          </div>
        </div>
        <div class="flex flex-wrap items-center justify-between gap-2 bg-slate-100/70 p-4">
          <RouterLink :to="{ name: 'projets-detail', params: { id: projet.id || projet.code } }" class="inline-flex items-center gap-1.5 rounded-lg bg-white px-3 py-2 text-xs font-semibold text-bleu-nuit hover:bg-slate-100"><Eye :size="15" />Détails</RouterLink>
          <div class="flex flex-wrap gap-2">
            <button v-if="peutGererProjets && !projet.archived" class="rounded-lg px-2 py-2 text-xs font-semibold text-bleu-nuit hover:bg-bleu-nuit/5" @click="openEditProject(projet)">Modifier</button>
            <button v-if="peutGererProjets && !projet.archived" class="rounded-lg px-2 py-2 text-xs font-semibold text-rose-baraka hover:bg-rose-baraka/10" @click="handleDeleteProject(projet.id)">Archiver</button>
          </div>
        </div>
      </article>
    </div>
    <div v-else-if="modeAffichage === 'cartes'" class="rounded-xl border border-bleu-nuit/10 bg-bleu-nuit/[0.035] p-10 text-center text-sm text-slate-500 backdrop-blur-xl">Aucun projet ne correspond aux filtres.</div>

    <nav v-if="pageCount > 1" class="flex items-center justify-between rounded-xl border border-bleu-nuit/10 bg-bleu-nuit/[0.035] px-4 py-3 text-sm backdrop-blur-xl" aria-label="Pagination des projets">
      <span class="text-slate-500">Page {{ currentPage }} sur {{ pageCount }} · {{ projectStore.pagination.count }} projet(s)</span>
      <div class="flex gap-2"><button :disabled="currentPage === 1" class="rounded-lg border px-3 py-2 disabled:opacity-40" @click="currentPage--">Precedent</button><button :disabled="currentPage === pageCount" class="rounded-lg border px-3 py-2 disabled:opacity-40" @click="currentPage++">Suivant</button></div>
    </nav>

    <!-- Modal Projet (Création & Modification) -->
    <ProjetFormModal
      v-if="peutGererProjets && modalOpen"
      :ouvert="modalOpen"
      :projet="editingProject"
      :saving="projectStore.loading"
      @fermer="closeModal"
      @save="handleSaveProject"
    />
  </div>
</template>

<script setup>
import { ref, computed, reactive, watch } from "vue"
import { RouterLink } from "vue-router"
import {
  Wallet,
  Activity,
  FolderKanban,
  Search,
  Plus,
  Eye,
  LayoutGrid,
  List,
} from "lucide-vue-next"
import ProjetFormModal from "@/modules/chef-projet/components/projets/ProjetFormModal.vue"
import BoutonPrimary from "@/components/ui/BoutonPrimary.vue"
import LoadingSpinner from "@/components/ui/LoadingSpinner.vue"
import AlertMessage from "@/components/ui/AlertMessage.vue"
import { useProjectStore } from "@/stores/project.js"
import { useAuthStore } from "@/stores/auth.js"

const projectStore = useProjectStore()
const authStore = useAuthStore()
const peutGererProjets = computed(() => authStore.user?.role === "GERANT")

const recherche = ref("")
const filtreStatut = ref("Tous les statuts")
const filtreRegion = ref("Toutes les régions")
const modalOpen = ref(false)
const editingProject = ref(null)
const feedback = reactive({ type: "success", message: "" })
const currentPage = ref(1)
const modeAffichage = ref("cartes")
const pageSize = 6

watch([currentPage, recherche, filtreStatut, filtreRegion], async () => {
  const params = { page: currentPage.value, page_size: pageSize, search: recherche.value.trim() }
  if (filtreStatut.value === "Actif") params.archived = "false"
  else if (filtreStatut.value === "Archivé") params.archived = "true"
  if (filtreRegion.value !== "Toutes les régions") params.region = filtreRegion.value
  try {
    await projectStore.fetchProjects(params)
  } catch (err) {
    feedback.type = "error"
    feedback.message = "Erreur lors du chargement des projets."
  }
}, { immediate: true })

const totalBudget = computed(() => {
  return projectStore.projects.reduce((acc, p) => acc + (parseFloat(p.budget) || 0), 0)
})

const activeProjectsCount = computed(() => {
  return projectStore.projects.filter((p) => !p.archived).length
})

const regionsList = computed(() => {
  const set = new Set(projectStore.projects.map((p) => p.region).filter(Boolean))
  return Array.from(set)
})

const projetsFiltres = computed(() => {
  return projectStore.projects
})

const pageCount = computed(() => Math.max(1, Math.ceil(projectStore.pagination.count / pageSize)))
const projetsPage = computed(() => projetsFiltres.value)
watch([recherche, filtreStatut, filtreRegion], () => { currentPage.value = 1 })
watch(pageCount, value => { if (currentPage.value > value) currentPage.value = value })

const formatBudget = (val) => {
  return new Intl.NumberFormat("fr-FR").format(val || 0) + " FCFA"
}

const openCreateModal = () => {
  editingProject.value = null
  modalOpen.value = true
}

const openEditProject = (projet) => {
  editingProject.value = projet
  modalOpen.value = true
}

const closeModal = () => {
  modalOpen.value = false
  editingProject.value = null
}

const handleSaveProject = async (payload) => {
  feedback.message = ""
  try {
    if (payload.id) {
      await projectStore.updateProject(payload.id, payload)
      feedback.type = "success"
      feedback.message = "Projet mis à jour avec succès !"
    } else {
      const currentUserId = authStore.user?.id
      await projectStore.createProject({
        ...payload,
        chef_projet: payload.chef_projet,
        responsable_finance: payload.responsable_finance,
      })
      feedback.type = "success"
      feedback.message = "Projet créé avec succès !"
    }
    closeModal()
    await projectStore.fetchProjects()
  } catch (err) {
    feedback.type = "error"
    feedback.message = projectStore.error || "Erreur lors de l'enregistrement du projet."
  }
}

const handleDeleteProject = async (id) => {
  if (!confirm("Voulez-vous vraiment archiver ce projet ?")) return
  try {
    await projectStore.archiveProject(id)
    feedback.type = "success"
    feedback.message = "Projet archivé avec succès."
  } catch (err) {
    feedback.type = "error"
    feedback.message = projectStore.error || "Impossible d'archiver ce projet."
  }
}
</script>
