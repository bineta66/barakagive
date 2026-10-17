<template>
  <div class="p-6 space-y-6 bg-white min-h-screen">
    <!-- En-tête -->
    <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 pb-4 border-b border-slate-100">
      <div>
        <h1 class="text-3xl font-bold text-bleu-nuit">Détail du projet</h1>
        <p class="text-sm text-gray-600 mt-1">
          Informations complètes du projet humanitaire.
        </p>
      </div>

      <div class="flex items-center gap-3">
        <BoutonSecondary to="/chef-projet/projets">
          <List :size="18" />
          Liste des projets
        </BoutonSecondary>

        <BoutonPrimary v-if="peutGererProjets && projet && !projet.archived" @click="editModalOpen = true">
          <Pencil :size="16" />
          Modifier le projet
        </BoutonPrimary>
      </div>
    </div>

    <LoadingSpinner v-if="loading" message="Chargement du projet..." />
    <AlertMessage v-if="feedback.message" :type="feedback.type" :message="feedback.message" class="mb-4" />

    <!-- Détails -->
    <div v-if="projet" class="bg-white border border-slate-200/60 rounded-xl p-6 shadow-xs-sm">
      <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div>
          <p class="text-xs font-bold uppercase text-slate-500 mb-1">Nom du projet</p>
          <p class="text-gray-800 text-lg font-semibold">{{ projet.name || projet.nom }}</p>
        </div>

        <div>
          <p class="text-xs font-bold uppercase text-slate-500 mb-1">Code</p>
          <p class="text-gray-700 font-mono">{{ projet.code }}</p>
        </div>

        <div>
          <p class="text-xs font-bold uppercase text-slate-500 mb-1">Région</p>
          <p class="text-gray-700">{{ projet.region || "Non spécifiée" }}</p>
        </div>

        <div>
          <p class="text-xs font-bold uppercase text-slate-500 mb-1">Budget alloué</p>
          <p class="text-gray-900 font-bold text-lg text-bleu-nuit">{{ formatBudget(projet.budget) }}</p>
        </div>

        <div>
          <p class="text-xs font-bold uppercase text-slate-500 mb-1">Statut</p>
          <span
            class="px-3 py-1 text-xs font-semibold rounded-full inline-block"
            :class="projet.archived ? 'bg-slate-100 text-slate-600' : 'bg-bleu-accent/10 text-bleu-accent'"
          >
            {{ projet.archived ? 'Archivé' : 'En cours' }}
          </span>
        </div>

        <div>
          <p class="text-xs font-bold uppercase text-slate-500 mb-1">Chef de projet</p>
          <p class="text-gray-700">{{ projet.chef_projet || "Assigné" }}</p>
        </div>

        <div>
          <p class="text-xs font-bold uppercase text-slate-500 mb-1">Date de début</p>
          <p class="text-gray-700">{{ projet.start_date || projet.debut || "-" }}</p>
        </div>

        <div>
          <p class="text-xs font-bold uppercase text-slate-500 mb-1">Date de fin</p>
          <p class="text-gray-700">{{ projet.end_date || projet.fin || "-" }}</p>
        </div>

        <div class="md:col-span-2">
          <p class="text-xs font-bold uppercase text-slate-500 mb-1">Objectif</p>
          <p class="text-gray-700">{{ projet.objectif || "Aucun objectif spécifié" }}</p>
        </div>

        <div class="md:col-span-2">
          <p class="text-xs font-bold uppercase text-slate-500 mb-1">Description</p>
          <p class="text-gray-700 whitespace-pre-line">{{ projet.description || "Aucune description fournie." }}</p>
        </div>
      </div>
      <div class="mt-6 border-t border-slate-100 pt-5">
        <div class="flex items-start justify-between gap-3">
          <div><h2 class="text-lg font-bold text-bleu-nuit">Criteres du projet</h2><p class="mt-1 text-sm text-slate-500">Criteres et poids utilises pour l'evaluation.</p></div>
          <span class="rounded-full bg-blue-50 px-3 py-1 text-xs font-semibold text-bleu-nuit">{{ criteresProjet.length }} critere(s)</span>
        </div>
        <div v-if="criteresProjet.length" class="mt-4 grid grid-cols-1 gap-2 md:grid-cols-2">
          <div v-for="critere in criteresProjet" :key="critere.id" class="flex items-start justify-between gap-4 rounded-lg border border-slate-100 bg-slate-50 p-3">
            <div><h3 class="text-sm font-semibold text-slate-800">{{ critere.nom }}</h3><p v-if="critere.vulnerable_values?.length" class="mt-1 text-xs text-slate-500">Reponses considerees : {{ critere.vulnerable_values.join(', ') }}</p></div>
            <span class="shrink-0 rounded-lg bg-blue-50 px-2.5 py-1 text-xs font-bold text-bleu-nuit">{{ critere.poids }} pts</span>
          </div>
        </div>
        <p v-else class="mt-4 rounded-lg bg-slate-50 p-4 text-sm text-slate-500">Aucun critere actif n'est configure pour ce projet.</p>
      </div>
    </div>

    <!-- Modal d'édition -->
    <section v-if="projet" class="grid grid-cols-1 gap-5">
      <article v-if="authStore.user?.role === 'CHEF_PROJET'" class="rounded-xl border border-blue-100 bg-white p-5 shadow-xs-sm">
        <div class="flex flex-wrap items-center justify-between gap-3">
          <div><h2 class="text-lg font-bold text-bleu-nuit">Résumé et propositions IA</h2><p class="mt-1 text-sm text-slate-500">L'analyse tient compte des critères du projet et des données agrégées.</p></div>
          <button :disabled="analysisLoading || projet.archived" class="inline-flex items-center gap-2 rounded-lg bg-bleu-nuit px-4 py-2.5 text-sm font-semibold text-white hover:bg-slate-700 disabled:opacity-50" @click="analyserProjet"><Sparkles :size="16" />{{ analysisLoading ? 'Analyse en cours...' : 'Analyser le projet' }}</button>
        </div>
        <AlertMessage v-if="analysisError" class="mt-4" type="error" :message="analysisError" />
        <div v-if="proposalReport" class="mt-4 space-y-4">
          <div class="rounded-lg bg-blue-50 p-4"><h3 class="text-sm font-bold text-bleu-nuit">Résumé IA</h3><p class="mt-2 whitespace-pre-line text-sm leading-relaxed text-slate-700">{{ proposalReport.analyse }}</p></div>
          <div v-if="proposalReport.propositions.length === refusedProposals.length" class="rounded-lg bg-slate-50 p-4 text-sm text-slate-600">Toutes les propositions ont été refusées.</div>
          <article v-for="(proposal, index) in proposalReport.propositions" :key="`${proposal.nom}-${index}`" class="rounded-lg border border-slate-200 p-4" :class="refusedProposals.includes(index) ? 'hidden' : ''">
            <div class="flex flex-wrap items-start justify-between gap-2"><div><h3 class="font-semibold text-slate-900">{{ proposal.nom }}</h3><p class="mt-1 text-xs font-medium text-bleu-nuit">{{ typeCampagneLabel(proposal.type) }}</p></div><span class="rounded-full bg-bleu-nuit/10 px-2.5 py-1 text-xs font-semibold text-bleu-nuit">À valider</span></div>
            <p class="mt-3 text-sm text-slate-700">{{ proposal.description }}</p>
            <p class="mt-2 text-xs text-slate-500">{{ proposal.date_debut }} au {{ proposal.date_fin }} · {{ proposal.zones.map(zone => zone.nom).join(', ') }}</p>
            <p class="mt-3 rounded-lg bg-slate-50 p-3 text-sm text-slate-700"><strong>Justification liée aux critères :</strong> {{ proposal.justification }}</p>
            <div class="mt-3 flex flex-wrap gap-2"><button class="rounded-lg bg-bleu-nuit px-3 py-2 text-xs font-semibold text-white hover:bg-slate-700" @click="validerProposition(proposal)">Valider et remplir le formulaire</button><button class="rounded-lg border border-slate-200 px-3 py-2 text-xs font-semibold text-slate-600 hover:bg-slate-50" @click="refuserProposition(index)">Refuser</button></div>
          </article>
        </div>
      </article>
    </section>

    <ProjetFormModal
      v-if="peutGererProjets && editModalOpen && projet"
      :ouvert="editModalOpen"
      :projet="projet"
      :saving="projectStore.loading"
      @fermer="editModalOpen = false"
      @save="handleSaveProject"
    />
  </div>
</template>

<script setup>
import { ref, computed, reactive, onMounted } from "vue"
import { useRoute, useRouter } from "vue-router"
import { List, Pencil, Sparkles } from "lucide-vue-next"
import api from "@/services/api.js"
import BoutonSecondary from "@/components/ui/BoutonSecondary.vue"
import BoutonPrimary from "@/components/ui/BoutonPrimary.vue"
import LoadingSpinner from "@/components/ui/LoadingSpinner.vue"
import AlertMessage from "@/components/ui/AlertMessage.vue"
import ProjetFormModal from "@/modules/chef-projet/components/projets/ProjetFormModal.vue"
import { useProjectStore } from "@/stores/project.js"
import { useAuthStore } from "@/stores/auth.js"

const route = useRoute()
const router = useRouter()
const projectStore = useProjectStore()
const authStore = useAuthStore()
const peutGererProjets = computed(() => authStore.user?.role === "GERANT")

const projet = ref(null)
const loading = ref(false)
const editModalOpen = ref(false)
const feedback = reactive({ type: "error", message: "" })
const criteresProjet = computed(() => projectStore.criteria || [])
const analysisLoading = ref(false)
const analysisError = ref("")
const proposalReport = ref(null)
const refusedProposals = ref([])

const formatBudget = (val) => {
  if (!val && val !== 0) return "0 FCFA"
  return new Intl.NumberFormat("fr-FR").format(val) + " FCFA"
}

const loadProject = async () => {
  loading.value = true
  feedback.message = ""
  const idOrCode = route.params.id
  try {
    if (!projectStore.projects.length) {
      await projectStore.fetchProjects()
    }
    const found = projectStore.projects.find((p) => String(p.id) === String(idOrCode) || p.code === idOrCode)
    if (found) {
      projet.value = found
    } else {
      const res = await projectStore.fetchProject(idOrCode)
      projet.value = res
    }
    await projectStore.fetchCriteria(projet.value.id)
  } catch (err) {
    feedback.type = "error"
    feedback.message = "Impossible de charger les détails du projet."
  } finally {
    loading.value = false
  }
}

const typeCampagneLabel = type => ({
  COLLECTE_BESOINS: "Collecte des besoins", DISTRIBUTION: "Distribution", SANTE: "Santé",
  ALIMENTATION: "Alimentation", EAU_HYGIENE: "Eau et hygiène", SENSIBILISATION: "Sensibilisation",
  URGENCE: "Urgence", SUIVI_EVALUATION: "Suivi et évaluation",
}[type] || type)

const analyserProjet = async () => {
  analysisLoading.value = true
  analysisError.value = ""
  proposalReport.value = null
  refusedProposals.value = []
  try {
    const response = await api.post(`/api/projects/${projet.value.id}/campaign-proposals/`)
    proposalReport.value = response.data
  } catch (err) {
    analysisError.value = err.response?.data?.detail || "L'analyse IA du projet est indisponible."
  } finally {
    analysisLoading.value = false
  }
}

const refuserProposition = index => {
  refusedProposals.value = [...new Set([...refusedProposals.value, index])]
}

const validerProposition = proposal => {
  router.push({ name: "campagnes-creer", query: {
    projet_id: String(projet.value.id), nom: proposal.nom, type: proposal.type,
    description: proposal.description, date_debut: proposal.date_debut,
    date_fin: proposal.date_fin, zone_ids: proposal.zones.map(zone => zone.id),
  } })
}

const handleSaveProject = async (payload) => {
  try {
    await projectStore.updateProject(projet.value.id, payload)
    feedback.type = "success"
    feedback.message = "Projet mis à jour avec succès !"
    editModalOpen.value = false
    await loadProject()
  } catch (err) {
    feedback.type = "error"
    feedback.message = projectStore.error || "Erreur lors de la mise à jour du projet."
  }
}

onMounted(loadProject)
</script>
