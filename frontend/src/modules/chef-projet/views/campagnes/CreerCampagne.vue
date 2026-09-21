<template>
  <div class="min-h-screen bg-white flex justify-center items-start py-8 px-4 sm:px-6 lg:px-8">
    <div class="w-full max-w-4xl bg-white rounded-2xl border border-slate-200/60 p-8 shadow-xs-sm">
      <div class="mb-6">
        <h2 class="text-3xl font-bold text-or">Créer une nouvelle campagne</h2>
        <p class="text-gray-600 text-sm mt-1">Configurez les paramètres de base et les zones de déploiement.</p>
      </div>

      <LoadingSpinner v-if="loadingInit" message="Chargement des projets et des zones..." />
      <AlertMessage v-if="feedback.message" :type="feedback.type" :message="feedback.message" class="mb-6" />

      <form v-if="!loadingInit" @submit.prevent="creerCampagne" class="space-y-8">
        <!-- Section 1 : Identification -->
        <div>
          <h3 class="text-xl font-bold text-or mb-4 pb-2 border-b">1. Identification</h3>

          <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div class="md:col-span-2">
              <label class="block text-sm font-semibold text-gray-700 mb-1">Nom de la campagne *</label>
              <input
                v-model="form.nom"
                type="text"
                required
                placeholder="Ex : Distribution Alimentaire d'Urgence Hivernage 2026"
                class="w-full rounded-lg border border-gray-300 bg-slate-50 px-4 py-2.5 focus:ring-2 focus:ring-or/30 outline-none text-sm"
              />
            </div>

            <div class="md:col-span-2">
              <label class="block text-sm font-semibold text-gray-700 mb-1">Projet humanitaire rattaché *</label>
              <select
                v-model="form.projet_id"
                required
                class="w-full rounded-lg border border-gray-300 bg-white px-4 py-2.5 focus:ring-2 focus:ring-or/30 outline-none text-sm"
              >
                <option value="">Sélectionner un projet parent...</option>
                <option v-for="p in projectStore.projects" :key="p.id" :value="p.id">
                  {{ p.name || p.nom }} ({{ p.code }})
                </option>
              </select>
            </div>

            <div class="md:col-span-2">
              <label class="block text-sm font-semibold text-gray-700 mb-1">Description</label>
              <textarea
                v-model="form.description"
                rows="3"
                placeholder="Décrivez succinctement l'objectif de la campagne..."
                class="w-full rounded-lg border border-gray-300 bg-slate-50 px-4 py-2.5 focus:ring-2 focus:ring-or/30 outline-none text-sm"
              ></textarea>
            </div>
          </div>
        </div>

        <!-- Section 2 : Zones d'intervention -->
        <div>
          <h3 class="text-xl font-bold text-or mb-4 pb-2 border-b">2. Zones d'intervention</h3>

          <div>
            <label class="block text-sm font-semibold text-gray-700 mb-2">
              Sélectionnez les zones d'intervention * (au moins une zone)
            </label>

            <div v-if="zoneStore.zones.length === 0" class="p-4 bg-slate-50 border rounded-lg text-sm text-slate-500">
              Aucune zone géographique configurée. Rendez-vous dans le menu "Zones" pour en créer une.
            </div>

            <div v-else class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-3 max-h-60 overflow-y-auto border rounded-lg p-3 bg-slate-50">
              <label
                v-for="z in zoneStore.zones"
                :key="z.id"
                class="flex items-center gap-2 p-2 rounded hover:bg-white cursor-pointer transition border border-transparent hover:border-slate-200"
              >
                <input
                  type="checkbox"
                  :value="z.id"
                  v-model="form.zone_ids"
                  class="rounded text-bleu-nuit focus:ring-or/30 w-4 h-4"
                />
                <span class="text-sm font-medium text-slate-800">{{ z.nom }}</span>
                <span class="text-xs text-slate-500">({{ z.region }})</span>
              </label>
            </div>
            <p class="text-xs text-slate-500 mt-1.5">
              {{ form.zone_ids.length }} zone(s) sélectionnée(s).
            </p>
          </div>
        </div>

        <!-- Section 3 : Calendrier -->
        <div>
          <h3 class="text-xl font-bold text-or mb-4 pb-2 border-b">3. Calendrier</h3>

          <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div>
              <label class="block text-sm font-semibold text-gray-700 mb-1">Date de début *</label>
              <input
                v-model="form.date_debut"
                type="date"
                required
                class="w-full rounded-lg border border-gray-300 bg-slate-50 px-4 py-2.5 text-sm"
              />
            </div>

            <div>
              <label class="block text-sm font-semibold text-gray-700 mb-1">Date de fin *</label>
              <input
                v-model="form.date_fin"
                type="date"
                required
                class="w-full rounded-lg border border-gray-300 bg-slate-50 px-4 py-2.5 text-sm"
              />
            </div>

            <div>
              <label class="block text-sm font-semibold text-gray-700 mb-1">Statut *</label>
              <select
                v-model="form.statut"
                required
                class="w-full rounded-lg border border-gray-300 bg-white px-4 py-2.5 text-sm"
              >
                <option value="BROUILLON">Brouillon</option>
                <option value="PLANIFIER">Planifiée</option>
                <option value="EN_COURS">En cours</option>
                <option value="TERMINE">Terminée</option>
                <option value="ANNULEE">Annulée</option>
              </select>
            </div>
          </div>
        </div>

        <!-- Section 4 : Affectation des agents terrain -->
        <div>
          <h3 class="text-xl font-bold text-or mb-4 pb-2 border-b">4. Affectation des agents terrain</h3>
          <p class="text-sm text-gray-600 mb-3">
            Sélectionnez les agents terrain puis les zones qui leurs sont affectées.
            Un agent peut intervenir dans plusieurs zones de la campagne.
          </p>

          <div v-if="campaignStore.agents.length === 0" class="p-4 bg-slate-50 border rounded-lg text-sm text-slate-500">
            Aucun agent terrain actif disponible pour votre ONG. Les agents doivent d'abord être créés par le Gérant.
          </div>

          <div v-else class="space-y-2 max-h-96 overflow-y-auto border rounded-lg p-3 bg-slate-50">
            <div
              v-for="agent in campaignStore.agents"
              :key="agent.id"
              class="rounded-lg bg-white border border-slate-200 p-3"
            >
              <label class="flex items-center gap-2 cursor-pointer">
                <input
                  type="checkbox"
                  :value="agent.id"
                  :checked="isAgentSelected(agent.id)"
                  @change="toggleAgent(agent.id)"
                  class="rounded text-bleu-nuit focus:ring-or/30 w-4 h-4"
                />
                <span class="text-sm font-medium text-slate-800">
                  {{ agent.full_name || (agent.first_name + " " + agent.last_name) }}
                </span>
                <span class="text-xs text-slate-500">({{ agent.role === "AGENT" ? "Agent" : "Chef" }})</span>
              </label>

              <!-- Zones affectées à cet agent (plusieurs possibles) -->
              <div v-if="isAgentSelected(agent.id)" class="mt-2 pl-6">
                <p v-if="zonesDisponibles.length === 0" class="text-xs text-slate-400 italic">
                  Sélectionnez d'abord les zones d'intervention (section 2).
                </p>
                <div v-else class="flex flex-wrap gap-x-4 gap-y-1.5">
                  <label
                    v-for="z in zonesDisponibles"
                    :key="z.id"
                    class="flex items-center gap-1.5 text-xs text-slate-700 cursor-pointer"
                  >
                    <input
                      type="checkbox"
                      :value="z.nom"
                      :checked="isZoneSelected(agent.id, z.nom)"
                      @change="toggleAgentZone(agent.id, z.nom)"
                      class="rounded text-bleu-nuit focus:ring-or/30 w-3.5 h-3.5"
                    />
                    {{ z.nom }}
                  </label>
                </div>
              </div>
            </div>
          </div>
          <p class="text-xs text-slate-500 mt-1.5">
            {{ agentsSelectionnes.length }} agent(s) sélectionné(s).
          </p>
        </div>

        <!-- Boutons d'action -->
        <div class="pt-6 border-t flex justify-end gap-4">
          <BoutonSecondary to="/chef-projet/campagnes" type="button">
            Annuler
          </BoutonSecondary>

          <button
            type="submit"
            :disabled="submitting || !form.zone_ids.length"
            class="px-6 py-2.5 bg-bleu-nuit text-white font-semibold text-sm rounded-lg hover:bg-[#01111eff] transition shadow-xs disabled:opacity-50"
          >
            {{ submitting ? "Création en cours..." : "Créer et activer la campagne" }}
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref, onMounted, computed } from "vue"
import { useRouter } from "vue-router"
import BoutonSecondary from "@/components/ui/BoutonSecondary.vue"
import LoadingSpinner from "@/components/ui/LoadingSpinner.vue"
import AlertMessage from "@/components/ui/AlertMessage.vue"
import { useCampaignStore } from "@/stores/campaign.js"
import { useProjectStore } from "@/stores/project.js"
import { useZoneStore } from "@/stores/zone.js"

const router = useRouter()
const campaignStore = useCampaignStore()
const projectStore = useProjectStore()
const zoneStore = useZoneStore()

const loadingInit = ref(true)
const submitting = ref(false)
const feedback = reactive({ type: "success", message: "" })

const form = reactive({
  nom: "",
  projet_id: "",
  description: "",
  zone_ids: [],
  date_debut: "",
  date_fin: "",
  // Affectation multi-zones : { [agentId]: [zoneNom, ...] }
  agentZones: {},
  statut: "PLANIFIER",
})

// Zones de la campagne (resolues depuis les ids selectionnes en section 2).
const zonesDisponibles = computed(() =>
  zoneStore.zones.filter((z) => form.zone_ids.includes(z.id))
)

// Agents ayant au moins une zone affectee.
const agentsSelectionnes = computed(() =>
  Object.entries(form.agentZones)
    .filter(([, zones]) => zones && zones.length > 0)
    .map(([id]) => Number(id))
)

function isAgentSelected(agentId) {
  return Array.isArray(form.agentZones[agentId])
}

function toggleAgent(agentId) {
  if (isAgentSelected(agentId)) {
    delete form.agentZones[agentId]
  } else {
    form.agentZones[agentId] = []
  }
}

function isZoneSelected(agentId, zoneNom) {
  return (form.agentZones[agentId] || []).includes(zoneNom)
}

function toggleAgentZone(agentId, zoneNom) {
  const zones = form.agentZones[agentId] || []
  const index = zones.indexOf(zoneNom)
  if (index === -1) {
    zones.push(zoneNom)
  } else {
    zones.splice(index, 1)
  }
  form.agentZones[agentId] = zones
}

onMounted(async () => {
  loadingInit.value = true
  try {
    await Promise.allSettled([
      projectStore.fetchProjects(),
      zoneStore.fetchZones(),
      campaignStore.fetchAgents(),
    ])
  } finally {
    loadingInit.value = false
  }
})

const creerCampagne = async () => {
  if (!form.zone_ids.length) {
    feedback.type = "error"
    feedback.message = "Veuillez sélectionner au moins une zone d'intervention."
    return
  }

  submitting.value = true
  feedback.message = ""

try {
    // Un agent peut etre affecte a plusieurs zones : on envoie la liste
    // complete de ses zones (une affectation creee par zone cote backend).
    const agents = Object.entries(form.agentZones)
      .filter(([, zones]) => zones && zones.length > 0)
      .map(([id, zones]) => ({
        agent_id: Number(id),
        zones,
        objectif: 0,
      }))

    if (agents.some((a) => a.zones.length === 0)) {
      feedback.type = "error"
      feedback.message = "Chaque agent sélectionné doit avoir au moins une zone."
      return
    }

    await campaignStore.createCampaign({
      nom: form.nom,
      projet_id: Number(form.projet_id),
      description: form.description,
      zone_ids: form.zone_ids,
      date_debut: form.date_debut,
      date_fin: form.date_fin,
      agents,
      statut: form.statut,
    })

    feedback.type = "success"
    feedback.message = "Campagne créée avec succès !"
    setTimeout(() => {
      router.push("/chef-projet/campagnes")
    }, 800)
  } catch (err) {
    feedback.type = "error"
    feedback.message = campaignStore.error || "Erreur lors de la création de la campagne."
  } finally {
    submitting.value = false
  }
}
</script>

