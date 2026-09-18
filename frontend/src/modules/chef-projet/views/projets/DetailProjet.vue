<template>
  <div class="p-6 space-y-6 bg-white min-h-screen">
    <!-- En-tête -->
    <div class="flex justify-between items-center pb-4">
      <div>
        <h1 class="text-3xl font-bold text-or">Détail du projet</h1>
        <p class="text-sm text-gray-600 mt-1">
          Informations complètes du projet humanitaire.
        </p>
      </div>

      <div class="flex gap-3">
        <BoutonSecondary to="/chef-projet/projets">
          <List :size="18" />
          Liste des projets
        </BoutonSecondary>
      </div>
    </div>

    <LoadingSpinner v-if="loading" message="Chargement du projet..." />
    <AlertMessage v-if="error" type="error" :message="error" class="mb-4" />

    <!-- Détails -->
    <div v-if="projet" class="bg-white border border-slate-200/60 rounded-xl p-6 shadow-xs-sm">
      <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div>
          <p class="text-xs font-bold uppercase text-slate-900 mb-1">Nom du projet</p>
          <p class="text-gray-800 text-lg font-semibold">{{ projet.name || projet.nom }}</p>
        </div>

        <div>
          <p class="text-xs font-bold uppercase text-slate-900 mb-1">Code</p>
          <p class="text-gray-700 font-mono">{{ projet.code }}</p>
        </div>

        <div>
          <p class="text-xs font-bold uppercase text-slate-900 mb-1">Région</p>
          <p class="text-gray-700">{{ projet.region || "Non spécifiée" }}</p>
        </div>

        <div>
          <p class="text-xs font-bold uppercase text-slate-900 mb-1">Budget alloué</p>
          <p class="text-gray-900 font-bold text-lg text-or">{{ formatBudget(projet.budget) }}</p>
        </div>

        <div>
          <p class="text-xs font-bold uppercase text-slate-900 mb-1">Statut</p>
          <span
            class="px-3 py-1 text-xs font-semibold rounded-full inline-block"
            :class="projet.archived ? 'bg-slate-100 text-slate-600' : 'bg-emerald-50 text-emerald-700'"
          >
            {{ projet.archived ? 'Archivé' : 'En cours' }}
          </span>
        </div>

        <div>
          <p class="text-xs font-bold uppercase text-slate-900 mb-1">Chef de projet</p>
          <p class="text-gray-700">{{ projet.chef_projet || "Assigné" }}</p>
        </div>

        <div>
          <p class="text-xs font-bold uppercase text-slate-900 mb-1">Date de début</p>
          <p class="text-gray-700">{{ projet.start_date || projet.debut || "-" }}</p>
        </div>

        <div>
          <p class="text-xs font-bold uppercase text-slate-900 mb-1">Date de fin</p>
           <p class="text-gray-700">{{ projet.end_date || projet.fin || "-" }}</p>
        </div>

        <div class="md:col-span-2">
          <p class="text-xs font-bold uppercase text-slate-900 mb-1">Objectif</p>
          <p class="text-gray-700">{{ projet.objectif || "Aucun objectif spécifié" }}</p>
        </div>

        <div class="md:col-span-2">
          <p class="text-xs font-bold uppercase text-slate-900 mb-1">Description</p>
          <p class="text-gray-700 whitespace-pre-line">{{ projet.description || "Aucune description fournie." }}</p>
        </div>
      </div>
    </div>
  </div>

  <OperationalOrbitalIA />
</template>

<script setup>
import { ref, onMounted } from "vue"
import { useRoute } from "vue-router"
import { List } from "lucide-vue-next"
import BoutonSecondary from "@/components/ui/BoutonSecondary.vue"
import LoadingSpinner from "@/components/ui/LoadingSpinner.vue"
import AlertMessage from "@/components/ui/AlertMessage.vue"
import OperationalOrbitalIA from "@/components/ia/OperationalOrbitalIA.vue"
import { useProjectStore } from "@/stores/project.js"

const route = useRoute()
const projectStore = useProjectStore()

const projet = ref(null)
const loading = ref(false)
const error = ref(null)

const formatBudget = (val) => {
  if (!val && val !== 0) return "0 FCFA"
  return new Intl.NumberFormat("fr-FR").format(val) + " FCFA"
}

onMounted(async () => {
  loading.value = true
  error.value = null
  const idOrCode = route.params.id
  try {
    if (!projectStore.projects.length) {
      await projectStore.fetchProjects()
    }
    const found = projectStore.projects.find((p) => String(p.id) === String(idOrCode) || p.code === idOrCode)
    if (found) {
      projet.value = found
    } else {
      // Direct fetch by id
      const res = await projectStore.fetchProject(idOrCode)
      projet.value = res
    }
  } catch (err) {
    error.value = "Impossible de charger les détails du projet."
  } finally {
    loading.value = false
  }
})
</script>

