<template>
  <div class="p-6 space-y-6 bg-white min-h-screen">
    <!-- En-tête -->
    <div class="flex justify-between items-center pb-4">
      <div>
        <h1 class="text-3xl font-bold text-or">Détail de la campagne</h1>
        <p class="text-sm text-gray-600 mt-1">
          Informations complètes de la campagne et gestion du formulaire de collecte.
        </p>
      </div>

      <div class="flex gap-3">
        <BoutonPrimary :to="`/chef-projet/campagnes/${route.params.id}/formulaire`">
          <FileText :size="18" />
          Formulaire dynamique
        </BoutonPrimary>

        <BoutonSecondary to="/chef-projet/campagnes">
          <List :size="18" />
          Liste des campagnes
        </BoutonSecondary>
      </div>
    </div>

    <LoadingSpinner v-if="loading" message="Chargement de la campagne..." />
    <AlertMessage v-if="error" type="error" :message="error" class="mb-4" />

    <!-- Détails -->
    <div class="max-w-3xl bg-white border border-slate-200/60 rounded-xl p-6 shadow-xs-sm" v-if="campagne">
      <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div>
          <p class="text-xs font-bold uppercase text-slate-900 mb-1">Nom de la campagne</p>
          <p class="text-gray-800 font-semibold text-lg">{{ campagne.nom }}</p>
        </div>

        <div>
          <p class="text-xs font-bold uppercase text-slate-900 mb-1">Code Campagne</p>
          <p class="text-gray-700 font-mono">{{ campagne.code_campagne }}</p>
        </div>

        <div>
          <p class="text-xs font-bold uppercase text-slate-900 mb-1">Projet rattaché</p>
          <p class="text-gray-700 font-medium">{{ campagne.projet?.name || "-" }}</p>
          <p class="text-xs text-gray-500">{{ campagne.projet?.code }}</p>
        </div>

        <div>
          <p class="text-xs font-bold uppercase text-slate-900 mb-1">Statut</p>
          <span
            class="px-2.5 py-1 text-xs font-semibold rounded-full inline-block"
            :class="badgeStatut(campagne.statut)"
          >
            {{ labelStatut(campagne.statut) }}
          </span>
        </div>

        <div>
          <p class="text-xs font-bold uppercase text-slate-900 mb-1">Date de début</p>
          <p class="text-gray-700">{{ campagne.date_debut || "Non définie" }}</p>
        </div>

        <div>
          <p class="text-xs font-bold uppercase text-slate-900 mb-1">Date de fin</p>
          <p class="text-gray-700">{{ campagne.date_fin || "Non définie" }}</p>
        </div>

        <div class="col-span-1 md:col-span-2">
          <p class="text-xs font-bold uppercase text-slate-900 mb-1">Zones d'intervention</p>
          <div v-if="campagne.zones?.length" class="flex flex-wrap gap-2 mt-1">
            <span
              v-for="z in campagne.zones"
              :key="z.id"
              class="px-2.5 py-1 bg-slate-100 text-slate-700 text-xs rounded-md border"
            >
              {{ z.nom }} ({{ z.region }})
            </span>
          </div>
          <p v-else class="text-gray-500 text-sm">Aucune zone assignée.</p>
        </div>

                <div class="col-span-1 md:col-span-2">
                  <p class="text-xs font-bold uppercase text-slate-900 mb-1">Description</p>
                  <p class="text-gray-700 whitespace-pre-line">{{ campagne.description || "Aucune description fournie." }}</p>
                </div>
              </div>
            </div>

            <!-- Gestion des affectations agents / zones -->
            <div v-if="campagne" class="max-w-3xl bg-white border-slate-200/60 rounded-xl p-6 shadow-xs-sm">
              <div class="flex items-start justify-between gap-3 mb-1">
                <div>
                  <h2 class="text-xl font-bold text-or">Affectation des agents aux zones</h2>
                  <p class="text-sm text-gray-600 mt-1">
                    Un agent peut intervenir dans plusieurs zones de la campagne.
                    Cochez les zones puis enregistrez pour chaque agent.
                  </p>
                </div>
                <button
                  @click="chargerAffectations"
                  class="p-2 text-slate-400 hover:text-slate-700 hover:bg-slate-100 rounded-full transition-colors"
                  title="Recharger"
                >
                  <RefreshCw :size="16" :class="loadingAffectations ? 'animate-spin' : ''" />
                </button>
              </div>

              <AlertMessage v-if="affectationFeedback.message" :type="affectationFeedback.type" :message="affectationFeedback.message" class="my-3" />

              <LoadingSpinner v-if="loadingAffectations" message="Chargement des affectations..." />

              <div v-else class="mt-4 space-y-4">
                <div v-if="zonesCampagne.length === 0" class="p-4 bg-slate-50 border rounded-lg text-sm text-slate-500">
                  Cette campagne n'a aucune zone d'intervention. Ajoutez des zones d'abord.
                </div>

                <template v-else>
                  <!-- Ajout / mise à jour d'un agent -->
                  <div class="rounded-xl border-slate-200 p-4 bg-slate-50/60">
                    <p class="text-xs font-bold uppercase text-slate-700 mb-2">Affecter un agent</p>
                    <select
                      v-model="selectedAgentId"
                      class="w-full border-slate-300 rounded-lg px-3 py-2 text-sm bg-white focus:ring-or/30 focus:border-or"
                    >
                      <option value="" disabled>Sélectionner un agent...</option>
                      <option v-for="agent in campaignStore.agents" :key="agent.id" :value="String(agent.id)">
                        {{ agent.full_name || [agent.first_name, agent.last_name].filter(Boolean).join(' ') }}
                      </option>
                    </select>

                    <div v-if="selectedAgentId" class="mt-3">
                      <p class="text-xs font-medium text-slate-600 mb-2">Zones affectées :</p>
                      <div class="flex flex-wrap gap-x-4 gap-y-2">
                        <label
                          v-for="zn in zonesCampagne"
                          :key="zn"
                          class="flex items-center gap-1.5 text-sm text-slate-700 cursor-pointer"
                        >
                          <input
                            type="checkbox"
                            :value="zn"
                            :checked="editZones.includes(zn)"
                            @change="toggleEditZone(zn)"
                            class="rounded text-bleu-nuit focus:ring-or/30 w-4 h-4"
                          />
                          {{ zn }}
                        </label>
                      </div>
                      <div class="mt-3 flex items-center gap-3">
                        <label class="text-xs text-slate-600">Objectif par zone</label>
                        <input
                          v-model.number="editObjectif"
                          type="number"
                          min="0"
                          class="w-28 border-slate-300 rounded-lg px-2 py-1 text-sm"
                        />
                        <button
                          @click="enregistrerAffectation"
                          :disabled="savingAffectation || editZones.length === 0"
                          class="ml-auto px-4 py-2 bg-bleu-nuit text-white text-sm font-semibold rounded-lg hover:bg-[#01111eff] disabled:opacity-50 transition"
                        >
                          {{ savingAffectation ? "Enregistrement..." : "Enregistrer" }}
                        </button>
                      </div>
                    </div>
                  </div>

                  <!-- Affectations actuelles -->
                  <div>
                    <p class="text-xs font-bold uppercase text-slate-700 mb-2">Agents affectés</p>
                    <div v-if="affectations.length === 0" class="text-sm text-slate-400 italic">
                      Aucun agent affecté pour le moment.
                    </div>
                    <div v-else class="space-y-2">
                      <div
                        v-for="aff in affectations"
                        :key="aff.agent.id"
                        class="rounded-lg border-slate-200 p-3 flex items-start justify-between gap-3"
                      >
                        <div class="min-w-0">
                          <p class="font-semibold text-slate-800 text-sm">{{ aff.agent.full_name }}</p>
                          <p class="text-xs text-slate-500">{{ aff.agent.email }}</p>
                          <div class="flex flex-wrap gap-1.5 mt-2">
                            <span
                              v-for="zn in aff.zones"
                              :key="zn"
                              class="px-2 py-0.5 bg-slate-100 text-slate-700 text-xs rounded-md border"
                            >
                              {{ zn }}
                            </span>
                          </div>
                        </div>
                        <button
                          @click="preparerEdition(aff)"
                          class="p-2 text-slate-400 hover:text-or hover:bg-slate-100 rounded-full transition-colors flex-shrink-0"
                          title="Modifier"
                        >
                          <Pencil :size="16" />
                        </button>
                      </div>
                    </div>
                  </div>
                </template>
              </div>
            </div>
         </div>
        </template>

<script setup>
import { ref, reactive, computed, onMounted } from "vue"
import { useRoute } from "vue-router"
import { List, FileText, RefreshCw, Pencil } from "lucide-vue-next"
import BoutonPrimary from "@/components/ui/BoutonPrimary.vue"
import BoutonSecondary from "@/components/ui/BoutonSecondary.vue"
import LoadingSpinner from "@/components/ui/LoadingSpinner.vue"
import AlertMessage from "@/components/ui/AlertMessage.vue"
import { useCampaignStore } from "@/stores/campaign.js"

const route = useRoute()
const campaignStore = useCampaignStore()

const campagne = ref(null)
const loading = ref(false)
const error = ref(null)

// ── Affectations agents / zones ──────────────────────────────
const affectations = ref([])
const zonesCampagne = ref([])
const loadingAffectations = ref(false)
const savingAffectation = ref(false)
const selectedAgentId = ref("")
const editZones = ref([])
const editObjectif = ref(0)
const affectationFeedback = reactive({ type: "success", message: "" })

const chargerAffectations = async () => {
  loadingAffectations.value = true
  affectationFeedback.message = ""
  try {
    const data = await campaignStore.fetchCampaignAffectations(route.params.id)
    affectations.value = data.affectations || []
    zonesCampagne.value = data.zones_campagne || []
  } catch (err) {
    affectationFeedback.type = "error"
    affectationFeedback.message = "Impossible de charger les affectations."
  } finally {
    loadingAffectations.value = false
  }
}

const toggleEditZone = (zoneNom) => {
  const index = editZones.value.indexOf(zoneNom)
  if (index === -1) {
    editZones.value.push(zoneNom)
  } else {
    editZones.value.splice(index, 1)
  }
}

const preparerEdition = (aff) => {
  selectedAgentId.value = String(aff.agent.id)
  editZones.value = [...(aff.zones || [])]
  editObjectif.value = aff.objectif || 0
}

const enregistrerAffectation = async () => {
  if (!selectedAgentId.value || editZones.value.length === 0) return
  savingAffectation.value = true
  affectationFeedback.message = ""
  try {
    await campaignStore.assignAgentZones(route.params.id, {
      agent_id: Number(selectedAgentId.value),
      zones: editZones.value,
      objectif: editObjectif.value || 0,
    })
    affectationFeedback.type = "success"
    affectationFeedback.message = "Affectations enregistrées avec succès."
    selectedAgentId.value = ""
    editZones.value = []
    editObjectif.value = 0
    await chargerAffectations()
  } catch (err) {
    affectationFeedback.type = "error"
    affectationFeedback.message =
      campaignStore.error || "Erreur lors de l'enregistrement des affectations."
  } finally {
    savingAffectation.value = false
  }
}

const statutCampagne = computed(() => labelStatut(campagne.value?.statut))

const labelStatut = (statut) => {
  switch (statut) {
    case "BROUILLON":
      return "Brouillon"
    case "PLANIFIER":
      return "Planifiée"
    case "EN_COURS":
      return "En cours"
    case "TERMINE":
      return "Terminée"
    case "ANNULEE":
      return "Annulée"
    default:
      return statut || "-"
  }
}

const badgeStatut = (statut) => {
  switch (statut) {
    case "EN_COURS":
      return "bg-emerald-50 text-emerald-700"
    case "PLANIFIER":
      return "bg-bleu-nuit text-white"
    case "TERMINE":
      return "bg-gray-500 text-white"
    case "ANNULEE":
      return "bg-red-100 text-red-800"
    case "BROUILLON":
      return "bg-amber-100 text-amber-800"
    default:
      return "bg-slate-100 text-slate-600"
  }
}

onMounted(async () => {
  loading.value = true
  error.value = null
  try {
    campagne.value = await campaignStore.fetchCampaign(route.params.id)
  } catch (err) {
    error.value = "Impossible de charger les détails de cette campagne."
  } finally {
    loading.value = false
  }

  // Charge les agents disponibles et les affectations actuelles.
  campaignStore.fetchAgents().catch(() => {})
  chargerAffectations()
})
</script>

