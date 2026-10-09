<template>
  <div
    class="min-h-screen bg-white flex justify-center items-start py-8 px-4 sm:px-6 lg:px-8"
  >
    <div
      class="w-full max-w-4xl bg-white rounded-2xl border border-slate-200/60 p-8 shadow-xs-sm"
    >
      <div class="mb-6">
        <h2 class="text-3xl font-bold text-bleu-nuit">
          Créer une nouvelle campagne
        </h2>
        <p class="text-gray-600 text-sm mt-1">
          Configurez les paramètres de base et les zones de déploiement.
        </p>
      </div>

      <LoadingSpinner
        v-if="loadingInit"
        message="Chargement des projets et des zones..."
      />
      <AlertMessage
        v-if="feedback.message"
        :type="feedback.type"
        :message="feedback.message"
        class="mb-6"
      />

      <form
        v-if="!loadingInit"
        @submit.prevent="creerCampagne"
        class="space-y-8"
      >
        <!-- Section 1 : Identification -->
        <div>
          <h3 class="text-xl font-bold text-bleu-nuit mb-4 pb-2 border-b">
            1. Identification
          </h3>

          <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div class="md:col-span-2">
              <label class="block text-sm font-semibold text-gray-700 mb-1"
                >Nom de la campagne *</label
              >
              <input
                v-model="form.nom" type="text" placeholder="Ex : Distribution Alimentaire d'Urgence Hivernage 2026" class="w-full rounded-lg border bg-slate-50 px-4 py-2.5 focus:ring-2 outline-none text-sm transition" :class="fErr.nom ? 'border-red-500 focus:ring-red-500/20' : 'border-gray-300 focus:ring-bleu-nuit/30'" maxlength="200"
              />
              <p v-if="fErr.nom" class="mt-1 text-xs text-red-600">{{ fErr.nom }}</p>
            </div>

            <div class="md:col-span-2">
              <label class="block text-sm font-semibold text-gray-700 mb-1"
                >Projet humanitaire rattaché *</label
              >
              <AsyncSearchSelect
                v-model="form.projet_id"
                endpoint="/api/projects/"
                label-key="name"
                value-key="id"
                secondary-key="code"
                placeholder="Rechercher un projet parent…"
              />
              <p v-if="fErr.projet_id" class="mt-1 text-xs text-red-600">{{ fErr.projet_id }}</p>
            </div>

            <div class="md:col-span-2">
              <label class="block text-sm font-semibold text-gray-700 mb-1"
                >Description</label
              >
              <textarea
                v-model="form.description"
                rows="3"
                maxlength="500"
                placeholder="Décrivez succinctement l'objectif de la campagne..."
                class="w-full rounded-lg border border-gray-300 bg-slate-50 px-4 py-2.5 focus:ring-2 focus:ring-bleu-nuit/30 outline-none text-sm"
              ></textarea>
              <p v-if="fErr.description" class="mt-1 text-xs text-red-600">{{ fErr.description }}</p>
            </div>

            <div class="md:col-span-2">
              <label class="block text-sm font-semibold text-gray-700 mb-1">Type d'opération *</label>
              <select v-model="form.type" required class="w-full rounded-lg border border-gray-300 bg-white px-4 py-2.5 text-sm focus:ring-2 focus:ring-bleu-nuit/30">
                <option value="" disabled>Sélectionner le type de campagne...</option>
                <option value="COLLECTE_BESOINS">Collecte des besoins</option>
                <option value="DISTRIBUTION">Distribution</option>
                <option value="SANTE">Santé</option>
                <option value="ALIMENTATION">Alimentation</option>
                <option value="EAU_HYGIENE">Eau et hygiène</option>
                <option value="SENSIBILISATION">Sensibilisation</option>
                <option value="URGENCE">Urgence</option>
                <option value="SUIVI_EVALUATION">Suivi et évaluation</option>
              </select>
              <p v-if="fErr.type" class="mt-1 text-xs text-red-600">{{ fErr.type }}</p>
              <p class="text-xs text-slate-500 mt-1">La collecte de fonds se gère dans le module Finance.</p>
            </div>
          </div>
        </div>

        <!-- Section 2 : Zones d'intervention -->
        <div>
          <h3 class="text-xl font-bold text-bleu-nuit mb-4 pb-2 border-b">
            2. Zones d'intervention
          </h3>

          <div>
            <label class="block text-sm font-semibold text-gray-700 mb-2">
              Sélectionnez les zones d'intervention * (au moins une zone)
            </label>

            <AsyncSearchMultiSelect
              v-model="form.zone_ids"
              endpoint="/api/zones/"
              label-key="nom"
              value-key="id"
              secondary-key="region_nom"
              placeholder="Rechercher des zones par nom…"
              @selected-options="selectedZoneOptions = $event"
              @resolved-ids="keepResolvedZoneIds"
            />
            <p v-if="fErr.zone_ids" class="mt-1 text-xs text-red-600">{{ fErr.zone_ids }}</p>
            <p class="text-xs text-slate-500 mt-1.5">
              {{ form.zone_ids.length }} zone(s) sélectionnée(s).
            </p>
          </div>
        </div>

        <!-- Section 3 : Calendrier -->
        <div>
          <h3 class="text-xl font-bold text-bleu-nuit mb-4 pb-2 border-b">
            3. Calendrier
          </h3>

          <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div>
              <label class="block text-sm font-semibold text-gray-700 mb-1"
                >Date de début *</label
              >
              <input
                v-model="form.date_debut" type="date" class="w-full rounded-lg border bg-slate-50 px-4 py-2.5 text-sm transition" :class="fErr.date_debut ? 'border-red-500' : 'border-gray-300'"
              />
              <p v-if="fErr.date_debut" class="mt-1 text-xs text-red-600">{{ fErr.date_debut }}</p>
            </div>

            <div>
              <label class="block text-sm font-semibold text-gray-700 mb-1"
                >Date de fin *</label
              >
              <input
                v-model="form.date_fin" type="date" class="w-full rounded-lg border bg-slate-50 px-4 py-2.5 text-sm transition" :class="fErr.date_fin ? 'border-red-500' : 'border-gray-300'"
              />
              <p v-if="fErr.date_fin" class="mt-1 text-xs text-red-600">{{ fErr.date_fin }}</p>
            </div>

            <div>
              <label class="block text-sm font-semibold text-gray-700 mb-1"
                >Statut *</label
              >
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
          <h3 class="text-xl font-bold text-bleu-nuit mb-4 pb-2 border-b">
            4. Affectation des agents terrain
          </h3>
          <p class="text-sm text-gray-600 mb-3">
            Sélectionnez les agents terrain puis les zones qui leurs sont
            affectées. Un agent peut intervenir dans plusieurs zones de la
            campagne.
          </p>

          <input
            v-model="agentSearch"
            type="search"
            placeholder="Rechercher un agent par nom, téléphone ou e-mail…"
            class="mb-3 w-full rounded-lg border border-slate-200 px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-bleu-nuit/30"
          />
          <div v-if="agentsSelectionnes.length" class="mb-3 flex flex-wrap gap-2">
            <span v-for="id in agentsSelectionnes" :key="id" class="inline-flex items-center gap-2 rounded-full bg-slate-100 px-3 py-1 text-xs text-slate-700">
              {{ agentLabels[id] || `Agent ${id}` }}
              <button type="button" class="font-bold" :aria-label="`Retirer ${agentLabels[id] || 'agent'}`" @click="toggleAgent(id)">×</button>
            </span>
          </div>

          <div
            v-if="campaignStore.agents.length === 0 && !agentSearch"
            class="p-4 bg-slate-50 border rounded-lg text-sm text-slate-500"
          >
            Aucun agent terrain actif disponible pour votre ONG. Les agents
            doivent d'abord être créés par le Gérant.
          </div>

          <div
            v-else-if="campaignStore.agents.length"
            class="space-y-2 max-h-96 overflow-y-auto border rounded-lg p-3 bg-slate-50"
          >
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
                  class="rounded text-bleu-nuit focus:ring-bleu-nuit/30 w-4 h-4"
                />
                <span class="text-sm font-medium text-slate-800">
                  {{
                    agent.full_name || agent.first_name + " " + agent.last_name
                  }}
                </span>
                <span class="text-xs text-slate-500"
                  >({{ agent.role === "AGENT" ? "Agent" : "Chef" }})</span
                >
              </label>

              <!-- Zones affectées à cet agent (plusieurs possibles) -->
              <div v-if="isAgentSelected(agent.id)" class="mt-2 pl-6">
                <p
                  v-if="zonesDisponibles.length === 0"
                  class="text-xs text-slate-400 italic"
                >
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
                      class="rounded text-bleu-nuit focus:ring-bleu-nuit/30 w-3.5 h-3.5"
                    />
                    {{ z.nom }}
                  </label>
                </div>
              </div>
            </div>
          </div>
          <p v-else class="p-4 text-sm text-slate-500">Aucun agent ne correspond à cette recherche.</p>
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
            {{
              submitting
                ? "Création en cours..."
                : "Créer et activer la campagne"
            }}
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref, onMounted, computed, watch } from "vue";
import { useRoute, useRouter } from "vue-router";
import BoutonSecondary from "@/components/ui/BoutonSecondary.vue";
import LoadingSpinner from "@/components/ui/LoadingSpinner.vue";
import AlertMessage from "@/components/ui/AlertMessage.vue";
import AsyncSearchSelect from "@/components/ui/AsyncSearchSelect.vue";
import AsyncSearchMultiSelect from "@/components/ui/AsyncSearchMultiSelect.vue";
import { useCampaignStore } from "@/stores/campaign.js";
import { useFormValidation, rules } from "@/composables/useFormValidation.js";

const router = useRouter();
const route = useRoute();
const campaignStore = useCampaignStore();
const { errors: fErr, validate: fValidate } = useFormValidation();

const loadingInit = ref(true);
const submitting = ref(false);
const feedback = reactive({ type: "success", message: "" });
const agentSearch = ref("");
const agentLabels = reactive({});
const selectedZoneOptions = ref([]);
let agentSearchTimer;

const form = reactive({
  nom: "",
  type: "",
  projet_id: "",
  description: "",
  zone_ids: [],
  date_debut: "",
  date_fin: "",
  agentZones: {},
  statut: "PLANIFIER",
});

const zonesDisponibles = computed(() => selectedZoneOptions.value);

watch(selectedZoneOptions, (zones) => {
  const validNames = new Set(zones.map((zone) => zone.nom));
  for (const [agentId, assignedZones] of Object.entries(form.agentZones)) {
    form.agentZones[agentId] = assignedZones.filter((zoneName) => validNames.has(zoneName));
  }
});

function keepResolvedZoneIds(validIds) {
  const valid = new Set(validIds.map(String));
  form.zone_ids = form.zone_ids.filter((id) => valid.has(String(id)));
}

const agentsSelectionnes = computed(() =>
  Object.entries(form.agentZones)
    .filter(([, zones]) => zones && zones.length > 0)
    .map(([id]) => Number(id))
);

function isAgentSelected(agentId) {
  return Array.isArray(form.agentZones[agentId]);
}
function isZoneSelected(agentId, zoneNom) {
  return (form.agentZones[agentId] || []).includes(zoneNom);
}

function toggleAgent(agentId) {
  if (isAgentSelected(agentId)) delete form.agentZones[agentId];
  else form.agentZones[agentId] = [];
}

async function chargerAgents(search = "") {
  const agents = await campaignStore.fetchAgents({ search, page: 1, page_size: 20 });
  for (const agent of agents || []) {
    agentLabels[agent.id] = agent.full_name || [agent.first_name, agent.last_name].filter(Boolean).join(" ");
  }
}

watch(agentSearch, (value) => {
  clearTimeout(agentSearchTimer);
  agentSearchTimer = setTimeout(() => chargerAgents(value.trim()).catch(() => {}), 250);
});

function toggleAgentZone(agentId, zoneNom) {
  const zones = form.agentZones[agentId] || [];
  const idx = zones.indexOf(zoneNom);
  if (idx === -1) zones.push(zoneNom);
  else zones.splice(idx, 1);
  form.agentZones[agentId] = zones;
}

onMounted(async () => {
  loadingInit.value = true;
  try {
    await Promise.allSettled([
      chargerAgents(),
    ]);
  } finally {
    loadingInit.value = false;
  }

  if (route.query.projet_id) form.projet_id = String(route.query.projet_id);
  if (route.query.nom) form.nom = String(route.query.nom);
  if (route.query.type) form.type = String(route.query.type);
  if (route.query.description) form.description = String(route.query.description);
  if (route.query.date_debut) form.date_debut = String(route.query.date_debut);
  if (route.query.date_fin) form.date_fin = String(route.query.date_fin);
  if (route.query.zone_ids) {
    const proposedIds = Array.isArray(route.query.zone_ids) ? route.query.zone_ids : [route.query.zone_ids];
    form.zone_ids = proposedIds.map(String);
  }
});

const creerCampagne = async () => {
  feedback.message = "";

  // Validation complète avant envoi
  const ok = fValidate({
    nom: [rules.nomCampagne, form.nom],
    projet_id: [rules.select, form.projet_id],
    type: [rules.select, form.type],
    description: [rules.description, form.description],
    date_debut: [rules.date, form.date_debut],
    date_fin: [rules.dateFin, form.date_fin, form.date_debut],
    zone_ids: [rules.required, form.zone_ids.length],
  });

  if (!ok) {
    feedback.type = "error";
    feedback.message = "Veuillez corriger les champs en rouge.";
    return;
  }

  if (!form.zone_ids.length) {
    fErr.zone_ids = "Sélectionnez au moins une zone d'intervention.";
    feedback.type = "error";
    feedback.message = "Veuillez corriger les champs en rouge.";
    return;
  }

  submitting.value = true;
  try {
    const agents = Object.entries(form.agentZones)
      .filter(([, zones]) => zones && zones.length > 0)
      .map(([id, zones]) => ({ agent_id: Number(id), zones, objectif: 0 }));

    await campaignStore.createCampaign({
      nom: form.nom.trim(),
      type: form.type,
      projet_id: Number(form.projet_id),
      description: form.description.trim(),
      zone_ids: form.zone_ids,
      date_debut: form.date_debut,
      date_fin: form.date_fin,
      agents,
      statut: form.statut,
    });

    feedback.type = "success";
    feedback.message = "Campagne créée avec succès !";
    setTimeout(() => router.push("/chef-projet/campagnes"), 800);
  } catch (err) {
    feedback.type = "error";
    feedback.message =
      campaignStore.error || "Erreur lors de la création de la campagne.";
  } finally {
    submitting.value = false;
  }
};
</script>

