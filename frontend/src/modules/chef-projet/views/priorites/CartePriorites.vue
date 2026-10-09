<template>
  <div class="flex flex-col" style="min-height: calc(100vh - 8rem)">
    <header class="grid grid-cols-1 gap-5 border-b border-slate-200/70 bg-white/70 px-5 py-5 backdrop-blur-xl sm:px-6 lg:grid-cols-[minmax(0,1fr)_auto] lg:items-end">
      <div class="min-w-0">
        <h1 class="text-2xl font-bold text-slate-900 flex items-center gap-2">
          <MapPinned class="text-bleu-nuit" :size="28" />
          Carte des priorités
        </h1>
        <div class="mt-4 grid grid-cols-1 gap-3 sm:grid-cols-2 xl:grid-cols-[minmax(180px,0.8fr)_minmax(220px,1.2fr)]">
          <label class="block text-xs font-semibold text-slate-500">
            Projet
            <select v-model="selectedProjectId" @change="onProjectChange" class="glass-control mt-1.5 w-full px-3 py-2.5 text-sm text-slate-800">
              <option value="">Tous les projets</option>
              <option v-for="project in projectsList" :key="project.id" :value="String(project.id)">{{ project.name || project.nom }}</option>
            </select>
          </label>
          <label class="block text-xs font-semibold text-slate-500">
            Campagne active
            <select v-model="selectedCampaignId" @change="onCampaignChange" class="glass-control mt-1.5 w-full px-3 py-2.5 text-sm text-slate-800">
              <option v-if="filteredCampaigns.length === 0" value="">Aucune campagne disponible</option>
              <option v-for="c in filteredCampaigns" :key="c.id" :value="String(c.id)">{{ c.nom }}</option>
            </select>
          </label>
        </div>
      </div>
      <div class="grid grid-cols-2 gap-2 sm:grid-cols-3 lg:min-w-[470px]">
        <div class="rounded-xl border border-white/80 bg-white/65 px-3.5 py-3 backdrop-blur-lg">
          <span class="block text-xs text-slate-500">Région sélectionnée</span>
          <span class="mt-1 block truncate font-semibold text-slate-800">{{ selectedRegion || "—" }}</span>
        </div>
        <div class="rounded-xl border border-white/80 bg-white/65 px-3.5 py-3 backdrop-blur-lg">
          <span class="block text-xs text-slate-500">Dernière mise à jour</span>
          <span class="mt-1 block font-semibold text-slate-800">{{ derniereMaj }}</span>
        </div>
        <div class="col-span-2 rounded-xl border border-white/80 bg-white/65 px-3.5 py-3 backdrop-blur-lg sm:col-span-1">
          <span class="block text-xs text-slate-500">Total bénéficiaires</span>
          <span class="mt-1 block text-lg font-bold text-bleu-nuit">{{ totalBeneficiaires }}</span>
        </div>
      </div>
    </header>

    <div class="flex-1 p-4 lg:p-6 grid grid-cols-1 lg:grid-cols-[minmax(0,7fr)_minmax(340px,3fr)] gap-4 min-h-0">
      <CarteSenegalPriorites
        :regions="allRegionsData"
        :zones="projectZones"
        :region-selectionnee="selectedRegion"
        :zone-selectionnee-id="selectedZoneId"
        :chargement="loadingScores"
        class="h-[420px] rounded-2xl border border-white/80 bg-white/55 p-4 backdrop-blur-lg lg:h-[calc(100vh-245px)] lg:min-h-[480px]"
        @region-selectionnee="selectRegion"
        @zone-selectionnee="selectZoneFromMap"
      />

      <aside class="flex h-[calc(100vh-245px)] min-h-[480px] flex-col overflow-hidden rounded-2xl border border-white/80 bg-white/65 backdrop-blur-lg">
        <!-- Vue 1 : Région -->
        <template v-if="!selectedBeneficiaire">
          <div class="px-5 py-4 border-b border-slate-100 flex items-start justify-between gap-3">
            <div class="min-w-0">
              <p class="text-xs font-semibold uppercase tracking-wider text-slate-400">
                {{ regionData ? "Assistant Projet · Région" : "Assistant Projet" }}
              </p>
              <h2 class="text-xl font-bold text-slate-900 truncate">
                {{ regionData?.region || selectedRegion || "Aucune sélection" }}
              </h2>
              <p v-if="regionData" class="text-sm text-slate-500 mt-1">
                {{ regionData.total_beneficiaires || 0 }} bénéficiaire{{ (regionData.total_beneficiaires || 0) > 1 ? "s" : "" }}
                • {{ (regionData.zones || []).length }} zone{{ (regionData.zones || []).length > 1 ? "s" : "" }}
              </p>
            </div>
            <span
              v-if="regionData"
              class="text-2xl font-black leading-none flex-shrink-0"
              :class="scoreColorClass(regionData.score_region)"
            >
              {{ regionData.score_region == null ? '—' : regionData.score_region }}
              <span class="block text-[10px] font-bold uppercase tracking-wider text-slate-400 mt-1">/ 100</span>
            </span>
          </div>

          <div v-if="loadingRegion" class="flex-1 flex items-center justify-center">
            <div class="animate-spin rounded-full h-9 w-9 border-b-2 border-bleu-nuit"></div>
          </div>

          <div v-else-if="regionError" class="flex-1 flex items-center justify-center px-8 text-center">
            <p class="text-sm text-red-600">{{ regionError }}</p>
          </div>

          <div v-else-if="campaignError && !activeCampaign" class="flex-1 flex items-center justify-center px-8 text-center">
            <p class="text-sm text-red-600">{{ campaignError }}</p>
          </div>

          <div v-else-if="!activeCampaign" class="flex-1 flex items-center justify-center px-8 text-center">
            <p class="text-sm text-slate-400">Aucune campagne en cours. Le panneau s’affichera dès qu’une campagne active est disponible.</p>
          </div>

          <div v-else-if="!selectedRegion" class="flex-1 flex items-center justify-center px-8 text-center">
            <p class="text-sm text-slate-400">Cliquez une région sur la carte pour afficher ses zones par ordre de priorité.</p>
          </div>

          <div v-else class="flex-1 overflow-y-auto">
            <!-- Résumé intelligent -->
            <div v-if="regionData?.summary" class="px-5 py-4 border-b border-slate-100 bg-bleu-nuit/5">
              <p class="text-xs font-bold uppercase tracking-wider text-bleu-nuit mb-1 flex items-center gap-1.5">
                <Sparkles :size="13" /> Résumé intelligent
              </p>
              <p class="text-sm text-slate-700 leading-relaxed">{{ regionData.summary }}</p>
            </div>

            <!-- Observations -->
            <div v-if="observations.length" class="px-5 py-4 border-b border-slate-100">
              <p class="text-xs font-bold uppercase tracking-wider text-slate-500 mb-2">Observations</p>
              <ul class="space-y-1.5">
                <li v-for="(obs, i) in observations" :key="i" class="flex items-start gap-2 text-sm text-slate-700">
                  <span class="mt-1.5 w-1.5 h-1.5 rounded-full bg-slate-400 flex-shrink-0"></span>
                  <span>{{ obs }}</span>
                </li>
              </ul>
            </div>

            <!-- Recommandations -->
            <div v-if="recommandations.length" class="px-5 py-4 border-b border-slate-100 bg-emerald-50/40">
              <p class="text-xs font-bold uppercase tracking-wider text-emerald-700 mb-2 flex items-center gap-1.5">
                <Lightbulb :size="13" /> Recommandations
              </p>
              <ul class="space-y-1.5">
                <li v-for="(rec, i) in recommandations" :key="i" class="flex items-start gap-2 text-sm text-slate-700">
                  <CheckCircle2 :size="15" class="text-emerald-600 mt-0.5 flex-shrink-0" />
                  <span>{{ rec }}</span>
                </li>
              </ul>
            </div>

            <div class="p-4 space-y-3">
              <h3 class="text-sm font-bold text-slate-800">Zones classées par priorité</h3>
              <CardZone
                v-for="(zone, index) in zonesTriees"
                :key="zone.id || zone.nom"
                :zone="zone"
                :rang="index + 1"
                :selected="String(zone.id) === String(selectedZoneId)"
                @voir-beneficiaire="openBeneficiaire"
                @selectionner-zone="focusZoneFromList"
              />
              <p v-if="zonesTriees.length === 0" class="text-sm text-slate-400 italic text-center py-6">
                Aucune zone prioritaire dans cette région.
              </p>
            </div>
          </div>
        </template>

        <!-- Vue 2 : Bénéficiaires d'une zone -->
        <template v-else-if="!selectedBeneficiaire.beneficiaireDetail">
          <div class="px-5 py-4 border-b border-slate-100 flex items-center gap-3">
            <button
              @click="closeZone"
              class="p-1.5 text-slate-400 hover:text-bleu-nuit hover:bg-bleu-nuit/10 rounded-lg transition"
            >
              <ArrowLeft :size="18" />
            </button>
            <div class="min-w-0">
              <h2 class="text-lg font-bold text-slate-900 truncate">{{ selectedZone?.nom }}</h2>
              <p class="text-sm text-slate-500">
                {{ beneficiariesOfSelectedZone.length }} bénéficiaire{{ beneficiariesOfSelectedZone.length > 1 ? "s" : "" }} classés
              </p>
            </div>
          </div>
          <div class="flex-1 overflow-y-auto p-4 space-y-2.5">
            <button
              v-for="b in beneficiariesOfSelectedZone"
              :key="b.id"
              @click="openBeneficiaire(b)"
              class="w-full text-left bg-white border border-slate-200/60 rounded-xl p-3.5 flex justify-between items-center hover:border-bleu-nuit/30 hover:bg-bleu-nuit/5 transition group"
            >
              <div class="flex items-center gap-3 min-w-0">
                <div class="h-11 w-11 rounded-full flex items-center justify-center font-bold flex-shrink-0" :class="avatarClass(b.score)">
                  {{ initials(b) }}
                </div>
                <div class="min-w-0">
                  <h4 class="font-semibold text-slate-900 truncate group-hover:text-bleu-nuit transition-colors">
                    {{ b.nom_complet }}
                  </h4>
                  <p class="text-xs text-slate-500 mt-0.5">
                    {{ b.sexe || "—" }} • {{ b.age ? b.age + " ans" : "Âge inconnu" }}
                    <template v-if="b.quartier"> • Quartier : {{ b.quartier }}</template>
                  </p>
                </div>
              </div>
              <div class="flex flex-col items-end flex-shrink-0">
                <span class="text-base font-black" :class="scoreColorClass(b.score)">
                  {{ b.score }}<span class="text-[10px] text-slate-400 font-semibold"> /100</span>
                </span>
                <span class="text-[10px] font-bold uppercase tracking-wider mt-0.5" :class="scoreColorClass(b.score)">
                  {{ niveauFromScore(b.score) }}
                </span>
              </div>
            </button>
            <p v-if="beneficiariesOfSelectedZone.length === 0" class="text-sm text-slate-400 italic text-center py-6">
              Aucun bénéficiaire dans cette zone.
            </p>
          </div>
        </template>

        <!-- Vue 3 : Fiche détaillée d'un bénéficiaire -->
        <template v-else>
          <BeneficiaireDetail
            :beneficiaire="selectedBeneficiaire"
            @back="closeBeneficiaire"
          />
        </template>
      </aside>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, nextTick } from "vue";
import { MapPinned, Sparkles, Lightbulb, CheckCircle2, ArrowLeft } from "lucide-vue-next";
import dayjs from "dayjs";
import api from "@/services/api.js";
import CarteSenegalPriorites from "@/modules/chef-projet/components/priorites/CarteSenegalPriorites.vue";
import CardZone from "@/modules/chef-projet/components/priorites/CardZone.vue";
import BeneficiaireDetail from "@/modules/chef-projet/components/priorites/BeneficiaireDetail.vue";

const activeCampaign = ref(null);
const campaignsList = ref([]);
const projectsList = ref([]);
const selectedProjectId = ref("");
const selectedCampaignId = ref(null);
const loadingScores = ref(false);
const loadingRegion = ref(false);
const allRegionsData = ref([]);
const selectedRegion = ref(null);
const regionData = ref(null);
const selectedZone = ref(null);
const selectedZoneId = ref(null);
const selectedBeneficiaire = ref(null);
const campaignError = ref(null);
const regionError = ref(null);
const lastLoadedAt = ref(null);

const derniereMaj = computed(() =>
  lastLoadedAt.value
    ? dayjs(lastLoadedAt.value).format("DD/MM/YYYY HH:mm")
    : dayjs().format("DD/MM/YYYY HH:mm")
);
const totalBeneficiaires = computed(() => {
  return allRegionsData.value.reduce((total, region) => total + (region.total_beneficiaires || 0), 0);
});
const projectZones = computed(() => allRegionsData.value.flatMap((region) =>
  (region.zones || []).map((zone) => ({ ...zone, region: zone.region || region.region }))
));

function projectIdFromCampaign(campaign) {
  return campaign?.projet?.id || campaign?.projet_id || campaign?.project?.id || campaign?.project_id || null;
}

function unwrapList(payload) {
  if (Array.isArray(payload)) return payload;
  if (Array.isArray(payload?.results)) return payload.results;
  return [];
}

function niveauFromScore(score) {
  if (score >= 80) return "Très élevée";
  if (score >= 60) return "Élevée";
  if (score >= 40) return "Moyenne";
  return "Faible";
}

function scoreColorClass(score) {
  if (score >= 80) return "text-red-600";
  if (score >= 60) return "text-orange-500";
  if (score >= 40) return "text-yellow-600";
  return "text-green-600";
}

function avatarClass(score) {
  if (score >= 80) return "bg-red-100 text-red-700";
  if (score >= 60) return "bg-orange-100 text-orange-700";
  if (score >= 40) return "bg-yellow-100 text-yellow-700";
  return "bg-green-100 text-green-700";
}

function initials(b) {
  const p = b.prenom || "";
  const n = b.nom || "";
  return ((p[0] || "") + (n[0] || "")).toUpperCase() || "?";
}

const zonesTriees = computed(() => {
  const zones = [...(regionData.value?.zones || [])];
  return zones
    .map((zone) => {
      const score = zone.score_moyen ?? null;
      const beneficiaires = [...(zone.beneficiaires || [])].sort(
        (a, b) => (b.score || 0) - (a.score || 0)
      );
      return {
        ...zone,
        score_moyen: score,
        niveau: zone.priorite_ia || zone.priorite || zone.niveau || "Information non disponible",
        total_beneficiaires: zone.total_beneficiaires ?? beneficiaires.length,
        beneficiaires,
      };
    })
    .sort((a, b) => (b.score_moyen || 0) - (a.score_moyen || 0));
});

const observations = computed(() => regionData.value?.observations || []);
const recommandations = computed(() => regionData.value?.recommandations || []);
const filteredCampaigns = computed(() => campaignsList.value.filter((campaign) => {
  return !selectedProjectId.value || String(projectIdFromCampaign(campaign)) === selectedProjectId.value;
}));

const beneficiariesOfSelectedZone = computed(() => {
  const zone = zonesTriees.value.find(
    (z) => z.id === selectedZone.value?.id || z.nom === selectedZone.value?.nom
  );
  return zone ? zone.beneficiaires || [] : [];
});

const fetchCampaign = async () => {
  campaignError.value = null;
  try {
    const campaignResponse = await api.get("/api/campaigns/");
    const campaigns = unwrapList(campaignResponse.data);
    campaignsList.value = campaigns;
    try {
      const projectsResponse = await api.get("/api/projects/", { params: { page_size: 100 } });
      projectsList.value = unwrapList(projectsResponse.data);
    } catch (projectError) {
      console.error("Erreur chargement projets pour les filtres", projectError);
      projectsList.value = [];
    }
    const active =
      campaigns.find((c) => (c.total_beneficiaires || 0) > 0 && c.statut === "EN_COURS") ||
      campaigns.find((c) => c.statut === "EN_COURS") ||
      campaigns.find((c) => (c.statut || "").toUpperCase().includes("COURS")) ||
      campaigns[0];
    if (active) {
      activeCampaign.value = active;
      selectedCampaignId.value = String(active.id);
      selectedProjectId.value = projectIdFromCampaign(active) ? String(projectIdFromCampaign(active)) : "";
      const projectId = projectIdFromCampaign(active);
      if (projectId) {
        await fetchAllRegionsData(projectId);
      } else {
        campaignError.value = "Cette campagne n’est liée à aucun projet.";
      }
    }
  } catch (error) {
    console.error("Erreur chargement campagne", error);
    campaignError.value = "Impossible de charger la campagne active.";
  }
};

const onCampaignChange = async () => {
  const chosen = campaignsList.value.find((c) => String(c.id) === String(selectedCampaignId.value));
  if (chosen) {
    activeCampaign.value = chosen;
    selectedProjectId.value = projectIdFromCampaign(chosen) ? String(projectIdFromCampaign(chosen)) : "";
    selectedRegion.value = null;
    regionData.value = null;
    const projectId = projectIdFromCampaign(chosen);
    if (projectId) {
      await fetchAllRegionsData(projectId);
    }
  }
};

const onProjectChange = async () => {
  const current = filteredCampaigns.value.find((campaign) => String(campaign.id) === String(selectedCampaignId.value));
  const chosen = current || filteredCampaigns.value.find((campaign) => (campaign.total_beneficiaires || 0) > 0) || filteredCampaigns.value[0];
  selectedCampaignId.value = chosen ? String(chosen.id) : "";
  activeCampaign.value = chosen || null;
  selectedRegion.value = null;
  regionData.value = null;
  allRegionsData.value = [];
  if (chosen && projectIdFromCampaign(chosen)) await fetchAllRegionsData(projectIdFromCampaign(chosen));
};

const fetchAllRegionsData = async (projectId) => {
  loadingScores.value = true;
  try {
    const response = await api.get(`/api/projets/${projectId}/regions/`);
    const regions = unwrapList(response.data);
    allRegionsData.value = regions.map((region) => ({
      region: region.region?.nom || region.region_name || region.region,
      score: region.score ?? region.score_region ?? 0,
      score_region: region.score_region ?? region.score ?? 0,
      total_beneficiaires: region.total_beneficiaires ?? 0,
      niveau: region.niveau || niveauFromScore(region.score ?? region.score_region ?? 0),
      couleur: region.couleur || "",
      zones: Array.isArray(region.zones) ? region.zones : [],
    }));
    lastLoadedAt.value = new Date();
    if (allRegionsData.value.length > 0 && !selectedRegion.value) {
      const topReg = allRegionsData.value.find((r) => (r.total_beneficiaires || 0) > 0);
      if (topReg) {
        selectRegion(topReg.region);
      }
    }
  } catch (error) {
    console.error("Erreur chargement données régions", error);
    allRegionsData.value = [];
    campaignError.value = "Impossible de charger les régions de ce projet.";
  } finally {
    loadingScores.value = false;
  }
};

const selectRegion = async (regionName, { keepZoneSelection = false } = {}) => {
  if (regionName === selectedRegion.value && regionData.value) return;

  selectedRegion.value = regionName;
  if (!keepZoneSelection) selectedZoneId.value = null;
  selectedZone.value = null;
  selectedBeneficiaire.value = null;
  regionData.value = null;
  regionError.value = null;

  if (!activeCampaign.value) {
    regionError.value = "Aucune campagne en cours pour afficher les priorités de cette région.";
    return;
  }

  const projectId = projectIdFromCampaign(activeCampaign.value);
  if (!projectId) {
    regionError.value = "Cette campagne n’est liée à aucun projet.";
    return;
  }

  loadingRegion.value = true;
  try {
    const response = await api.get(
      `/api/projets/${projectId}/regions/${encodeURIComponent(regionName)}/priorites/`
    );
    regionData.value = response.data;
    lastLoadedAt.value = new Date();
    if (allRegionsData.value.length > 0 && !selectedRegion.value) {
      const topReg = allRegionsData.value.find((r) => (r.total_beneficiaires || 0) > 0) || allRegionsData.value[0];
      if (topReg) {
        selectRegion(topReg.region);
      }
    }
  } catch (error) {
    console.error("Erreur chargement détails région", error);
    regionError.value = `Impossible de charger les données de ${regionName}.`;
  } finally {
    loadingRegion.value = false;
  }
};

const focusZoneFromList = (zone) => {
  selectedZoneId.value = String(zone.id);
};

const selectZoneFromMap = async (zone) => {
  selectedZoneId.value = String(zone.id);
  if (zone.region && zone.region !== selectedRegion.value) {
    await selectRegion(zone.region, { keepZoneSelection: true });
  }
  await nextTick();
  document.getElementById(`priority-zone-${zone.id}`)?.scrollIntoView({ block: "nearest" });
};

const openZone = (zone) => {
  selectedZone.value = zone;
  selectedBeneficiaire.value = null;
};

const closeZone = () => {
  selectedZone.value = null;
};

const openBeneficiaire = (beneficiaire) => {
  selectedBeneficiaire.value = {
    ...beneficiaire,
    beneficiaireDetail: true,
    criteres_detail: beneficiaire.criteres_detail || beneficiaire.criteres || [],
  };
};

const closeBeneficiaire = () => {
  selectedBeneficiaire.value = null;
};

onMounted(() => {
  fetchCampaign();
});
</script>
