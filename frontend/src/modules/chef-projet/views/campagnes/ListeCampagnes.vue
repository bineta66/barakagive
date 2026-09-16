<template>
  <div class="p-6 space-y-6 bg-white min-h-screen">
    <!-- Titre -->
    <div class="flex justify-between items-center pb-4">
      <div>
        <h1 class="text-4xl font-bold text-or">Campagnes</h1>
        <p class="text-xs text-gray-500 mt-1">
          Gérez et suivez les campagnes humanitaires.
        </p>
      </div>

      <BoutonPrimary to="/chef-projet/campagnes/creer">
        <Plus :size="18" />
        Nouvelle campagne
      </BoutonPrimary>
    </div>

    <LoadingSpinner v-if="campaignStore.loading && !campaignStore.campaigns.length" message="Chargement des campagnes..." />
    <AlertMessage v-if="feedback.message" :type="feedback.type" :message="feedback.message" class="mb-4" />

    <!-- Cartes statistiques -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
      <div class="bg-white border border-slate-200/60 shadow-xs rounded-xl p-4 flex justify-between">
        <div>
          <p class="text-xs font-bold uppercase text-slate-900">Total campagnes</p>
          <h3 class="text-xl font-bold text-or mt-2">{{ statistiques.total }}</h3>
        </div>
        <ClipboardList class="text-bleu-nuit" :size="28" />
      </div>

      <div class="bg-white border border-slate-200/60 shadow-xs rounded-xl p-4 flex justify-between">
        <div>
          <p class="text-xs font-bold uppercase text-slate-900">Actives</p>
          <h3 class="text-xl font-bold text-or mt-2">{{ statistiques.actives }}</h3>
        </div>
        <Activity class="text-bleu-nuit" :size="28" />
      </div>

      <div class="bg-white border border-slate-200/60 shadow-xs rounded-xl p-4 flex justify-between">
        <div>
          <p class="text-xs font-bold uppercase text-slate-900">Terminées</p>
          <h3 class="text-xl font-bold text-or mt-2">{{ statistiques.terminees }}</h3>
        </div>
        <CheckCircle class="text-bleu-nuit" :size="28" />
      </div>
    </div>

    <!-- Filtres -->
    <div class="bg-white border border-slate-200/60 shadow-xs rounded-xl p-4 grid md:grid-cols-3 gap-3">
      <div class="relative">
        <Search class="absolute left-3 top-3 text-slate-400" :size="16" />
        <input
          v-model="recherche"
          type="text"
          placeholder="Rechercher une campagne..."
          class="w-full border rounded-lg pl-9 pr-3 py-2 text-sm outline-none focus:ring-2 focus:ring-or/30"
        />
      </div>

      <select
        v-model="filtreStatut"
        class="border rounded-lg px-3 py-2 text-sm bg-white"
      >
        <option value="Tous les statuts">Tous les statuts</option>
        <option value="En cours">En cours</option>
        <option value="Planifiée">Planifiée</option>
        <option value="Terminée">Terminée</option>
      </select>

      <select
        v-model="filtreProjet"
        class="border rounded-lg px-3 py-2 text-sm bg-white"
      >
        <option value="Tous les projets">Tous les projets</option>
        <option v-for="proj in projectStore.projects" :key="proj.id" :value="proj.name">
          {{ proj.name }}
        </option>
      </select>
    </div>

    <!-- Tableau -->
    <div class="bg-white rounded-xl border border-slate-200/60 overflow-x-auto">
      <table class="w-full min-w-[640px]">
        <thead class="bg-slate-50 text-xs uppercase text-bleu-nuit">
          <tr>
            <th class="text-left px-4 py-4">Campagne</th>
            <th class="text-left px-4">Projet</th>
            <th class="text-left px-4">Zones</th>
            <th class="text-left px-4">Statut</th>
            <th class="text-right px-4">Actions</th>
          </tr>
        </thead>

        <tbody>
          <tr v-for="campagne in campagnesPage" :key="campagne.id" class="border-t hover:bg-slate-50">
            <td class="px-4 py-4">
              <h3 class="font-semibold text-sm text-slate-800">
                {{ campagne.nom }}
              </h3>
              <p class="text-xs text-gray-500">{{ campagne.code }}</p>
            </td>

            <td class="px-4 text-sm text-slate-600">
              {{ campagne.projet }}
            </td>

            <td class="px-4 text-sm text-slate-600">
              {{ campagne.zone }}
            </td>

            <td class="px-4">
              <StatusBadge :statut="campagne.statut">{{ campagne.statut }}</StatusBadge>
            </td>

            <td class="px-4">
              <div class="flex justify-end gap-2">
                <RouterLink :to="`/chef-projet/campagnes/${campagne.id}`" class="text-slate-500 hover:text-bleu-nuit p-1" title="Voir détails">
                  <Eye :size="18" />
                </RouterLink>

                <RouterLink :to="`/chef-projet/campagnes/modifier/${campagne.id}`" class="text-slate-500 hover:text-or p-1" title="Modifier">
                  <Pencil :size="18" />
                </RouterLink>

                <RouterLink :to="`/chef-projet/campagnes/${campagne.id}/formulaire`" class="text-slate-500 hover:text-bleu-nuit p-1" title="Formulaire dynamique">
                  <FileText :size="18" />
                </RouterLink>

                <button
                  @click="supprimerCampagne(campagne.id)"
                  class="text-slate-500 hover:text-red-600 p-1"
                  title="Supprimer"
                >
                  <Archive :size="18" />
                </button>
              </div>
            </td>
          </tr>

          <tr v-if="!campagnesPage.length">
            <td colspan="5" class="py-8 text-center text-sm text-slate-500">
              Aucune campagne trouvée.
            </td>
          </tr>
        </tbody>
      </table>

      <!-- Pagination -->
      <div v-if="campagnesFiltrees.length > 0" class="flex items-center justify-between px-4 py-3 border-t text-xs">
        <p class="text-slate-500">
          Affichage de {{ campagnesPage.length }} sur {{ campagnesFiltrees.length }} campagnes
        </p>

        <div class="flex gap-1" v-if="totalPages > 1">
          <button
            class="px-3 py-2 border rounded bg-slate-100 text-slate-400"
            :disabled="pageCourante === 1"
            @click="pageCourante = pageCourante - 1"
          >
            Précédent
          </button>

          <button
            v-for="page in totalPages"
            :key="page"
            class="w-8 h-8 border rounded"
            :class="page === pageCourante ? 'bg-bleu-nuit text-white' : ''"
            @click="pageCourante = page"
          >
            {{ page }}
          </button>

          <button
            class="px-3 py-2 border rounded"
            :disabled="pageCourante === totalPages"
            @click="pageCourante = pageCourante + 1"
          >
            Suivant
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { reactive, onMounted } from "vue"
import { RouterLink } from "vue-router"
import StatusBadge from "@/components/ui/StatusBadge.vue"
import LoadingSpinner from "@/components/ui/LoadingSpinner.vue"
import AlertMessage from "@/components/ui/AlertMessage.vue"
import { useCampagnes } from "@/composables/useCampagnes.js"
import { useProjectStore } from "@/stores/project.js"
import { Plus, ClipboardList, Activity, CheckCircle, Search, Eye, Pencil, Archive, FileText } from "lucide-vue-next"
import BoutonPrimary from "@/components/ui/BoutonPrimary.vue"

const projectStore = useProjectStore()
const feedback = reactive({ type: "success", message: "" })

const {
  recherche,
  filtreStatut,
  filtreProjet,
  filtreZone,
  pageCourante,
  campagnesPage,
  totalPages,
  campagnesFiltrees,
  statistiques,
  campaignStore,
} = useCampagnes()

onMounted(async () => {
  try {
    await projectStore.fetchProjects()
  } catch (e) {}
})

const supprimerCampagne = async (id) => {
  if (!confirm("Êtes-vous sûr de vouloir supprimer cette campagne ?")) return
  feedback.message = ""
  try {
    await campaignStore.deleteCampaign(id)
    feedback.type = "success"
    feedback.message = "Campagne supprimée avec succès."
  } catch (err) {
    feedback.type = "error"
    feedback.message = campaignStore.error || "Erreur lors de la suppression de la campagne."
  }
}
</script>

