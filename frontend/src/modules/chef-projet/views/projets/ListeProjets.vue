<template>
  <div class="p-6 space-y-6 bg-white min-h-screen">
    <!-- Titre -->
    <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 pb-4">
      <div>
        <h1 class="text-4xl font-bold text-or">Projets</h1>
        <p class="text-xs text-gray-500 mt-1">
          Gérez et suivez les projets humanitaires sur le terrain et en phase de déploiement.
        </p>
      </div>

      <button
        v-if="authStore.role !== 'CHEF_PROJET'"
        @click="showCreateModal = true"
        class="inline-flex items-center gap-2 px-4 py-2.5 bg-bleu-nuit text-white text-sm font-semibold rounded-lg hover:bg-[#01111eff] transition shadow-xs"
      >
        <Plus :size="18" />
        Nouveau projet
      </button>
    </div>

    <!-- Alert and Loading -->
    <LoadingSpinner v-if="projectStore.loading && !projectStore.projects.length" message="Chargement des projets..." />
    <AlertMessage v-if="feedback.message" :type="feedback.type" :message="feedback.message" class="mb-4" />

    <!-- Cartes statistiques -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
      <div class="bg-white border border-slate-200/60 shadow-xs rounded-xl p-4 flex justify-between">
        <div>
          <p class="text-xs font-bold uppercase text-slate-900">Volume budgétaire alloué</p>
          <h3 class="text-xl font-bold text-or mt-2">{{ formatBudget(totalBudget) }}</h3>
        </div>
        <Wallet class="text-bleu-nuit" :size="28" />
      </div>

      <div class="bg-white border border-slate-200/60 shadow-xs rounded-xl p-4 flex justify-between">
        <div>
          <p class="text-xs font-bold uppercase text-slate-900">Projets actifs</p>
          <h3 class="text-xl font-bold text-or mt-2">{{ activeProjectsCount }}</h3>
        </div>
        <Activity class="text-bleu-nuit" :size="28" />
      </div>

      <div class="bg-white border border-slate-200/60 shadow-xs rounded-xl p-4 flex justify-between">
        <div>
          <p class="text-xs font-bold uppercase text-slate-900">Total projets</p>
          <h3 class="text-xl font-bold text-slate-800 mt-2">{{ projectStore.projects.length }}</h3>
        </div>
        <FolderKanban class="text-bleu-nuit" :size="28" />
      </div>
    </div>

    <!-- Filtres -->
    <div class="bg-white border border-slate-200/60 shadow-xs rounded-xl p-4 grid md:grid-cols-3 gap-3">
      <select v-model="filtreStatut" class="border rounded-lg px-3 py-2 text-sm bg-white">
        <option value="Tous les statuts">Tous les statuts</option>
        <option value="Actif">Actifs</option>
        <option value="Archivé">Archivés</option>
      </select>

      <select v-model="filtreRegion" class="border rounded-lg px-3 py-2 text-sm bg-white">
        <option value="Toutes les régions">Toutes les régions</option>
        <option v-for="reg in regionsList" :key="reg" :value="reg">{{ reg }}</option>
      </select>

      <div class="relative">
        <Search class="absolute left-3 top-3 text-slate-400" :size="16" />
        <input
          v-model="recherche"
          type="text"
          placeholder="Rechercher un projet..."
          class="w-full border rounded-lg pl-9 pr-3 py-2 text-sm"
        />
      </div>
    </div>

    <!-- Tableau -->
    <TableauProjets
      :projects="projetsFiltres"
      :can-manage="authStore.role !== 'CHEF_PROJET'"
      @delete="handleDeleteProject"
    />

    <!-- Modal Création Projet -->
    <div
      v-if="showCreateModal && authStore.role !== 'CHEF_PROJET'"
      class="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4"
    >
      <div class="bg-white border border-slate-200 rounded-2xl max-w-lg w-full p-6 shadow-xs-sm space-y-4 max-h-[90vh] overflow-y-auto">
        <div class="flex justify-between items-center border-b pb-3">
          <h3 class="text-lg font-bold text-bleu-nuit">Créer un nouveau projet</h3>
          <button @click="showCreateModal = false" class="text-gray-400 hover:text-gray-600 text-xl font-bold">×</button>
        </div>

        <form @submit.prevent="submitCreateProject" class="space-y-4">
          <div>
            <label class="block text-xs font-bold uppercase text-slate-700 mb-1">Nom du projet *</label>
            <input
              v-model="newProject.name"
              type="text"
              required
              placeholder="Ex: Secours Alimentaire & Nutrition d'Urgence"
              class="w-full border rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-or/30 outline-none"
            />
          </div>

          <div>
            <label class="block text-xs font-bold uppercase text-slate-700 mb-1">Région *</label>
            <select
              v-model="newProject.region"
              required
              class="w-full border rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-or/30 outline-none"
            >
              <option value="">Sélectionner une région</option>
              <option v-for="r in senegalRegions" :key="r" :value="r">{{ r }}</option>
            </select>
          </div>

          <div>
            <label class="block text-xs font-bold uppercase text-slate-700 mb-1">Objectif *</label>
            <textarea
              v-model="newProject.objectif"
              rows="2"
              required
              placeholder="Objectif principal du projet..."
              class="w-full border rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-or/30 outline-none"
            ></textarea>
          </div>

          <div>
            <label class="block text-xs font-bold uppercase text-slate-700 mb-1">Description</label>
            <textarea
              v-model="newProject.description"
              rows="2"
              placeholder="Description détaillée..."
              class="w-full border rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-or/30 outline-none"
            ></textarea>
          </div>

          <div class="grid grid-cols-2 gap-3">
            <div>
              <label class="block text-xs font-bold uppercase text-slate-700 mb-1">Date début *</label>
              <input
                v-model="newProject.start_date"
                type="date"
                required
                class="w-full border rounded-lg px-3 py-2 text-sm"
              />
            </div>
            <div>
              <label class="block text-xs font-bold uppercase text-slate-700 mb-1">Date fin *</label>
              <input
                v-model="newProject.end_date"
                type="date"
                required
                class="w-full border rounded-lg px-3 py-2 text-sm"
              />
            </div>
          </div>

          <div class="flex justify-end gap-3 pt-3 border-t">
            <button
              type="button"
              @click="showCreateModal = false"
              class="px-4 py-2 border rounded-lg text-sm text-slate-600 hover:bg-slate-50"
            >
              Annuler
            </button>
            <button
              type="submit"
              :disabled="saving"
              class="px-5 py-2 bg-bleu-nuit text-white text-sm font-semibold rounded-lg hover:bg-[#01111eff] disabled:opacity-50"
            >
              {{ saving ? "Création..." : "Créer le projet" }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, reactive, onMounted } from "vue"
import {
  Wallet,
  Activity,
  FolderKanban,
  Search,
  Plus,
} from "lucide-vue-next"
import TableauProjets from "@/modules/chef-projet/components/projets/TableauProjets.vue"
import LoadingSpinner from "@/components/ui/LoadingSpinner.vue"
import AlertMessage from "@/components/ui/AlertMessage.vue"
import { useProjectStore } from "@/stores/project.js"
import { useAuthStore } from "@/stores/auth.js"

const projectStore = useProjectStore()
const authStore = useAuthStore()

const recherche = ref("")
const filtreStatut = ref("Tous les statuts")
const filtreRegion = ref("Toutes les régions")
const showCreateModal = ref(false)
const saving = ref(false)
const feedback = reactive({ type: "success", message: "" })

const senegalRegions = [
  "Dakar", "Thiès", "Diourbel", "Fatick", "Kaolack", "Kaffrine",
  "Saint-Louis", "Louga", "Matam", "Tambacounda", "Kédougou",
  "Kolda", "Sédhiou", "Ziguinchor"
]

const newProject = reactive({
  name: "",
  description: "",
  region: "",
  objectif: "",
  start_date: "",
  end_date: "",
})

onMounted(async () => {
  try {
    await projectStore.fetchProjects()
  } catch (err) {
    feedback.type = "error"
    feedback.message = "Erreur lors du chargement des projets."
  }
})

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
  return projectStore.projects.filter((p) => {
    const q = recherche.value.toLowerCase()
    const nameMatch = (p.name || p.nom || "").toLowerCase().includes(q)
    const codeMatch = (p.code || "").toLowerCase().includes(q)
    const okRecherche = !q || nameMatch || codeMatch

    let okStatut = true
    if (filtreStatut.value === "Actif") okStatut = !p.archived
    else if (filtreStatut.value === "Archivé") okStatut = !!p.archived

    let okRegion = true
    if (filtreRegion.value !== "Toutes les régions") {
      okRegion = p.region === filtreRegion.value
    }

    return okRecherche && okStatut && okRegion
  })
})

const formatBudget = (val) => {
  return new Intl.NumberFormat("fr-FR").format(val) + " FCFA"
}

const submitCreateProject = async () => {
  saving.value = true
  feedback.message = ""
  try {
    const currentUserId = authStore.user?.id
    await projectStore.createProject({
      ...newProject,
      chef_projet: currentUserId,
      responsable_finance: currentUserId,
    })
    feedback.type = "success"
    feedback.message = "Projet créé avec succès !"
    showCreateModal.value = false
    Object.assign(newProject, {
      name: "",
      description: "",
      region: "",
      objectif: "",
      start_date: "",
      end_date: "",
    })
  } catch (err) {
    feedback.type = "error"
    feedback.message = projectStore.error || "Erreur lors de la création du projet."
  } finally {
    saving.value = false
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


