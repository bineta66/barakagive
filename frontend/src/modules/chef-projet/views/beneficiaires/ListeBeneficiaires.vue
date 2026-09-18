<template>
  <div class="p-6 bg-white min-h-screen">
    <div class="space-y-4">
      <!-- En-tête -->
      <div class="flex justify-between items-center pb-4">
        <div>
          <h1 class="text-3xl font-bold text-or">Bénéficiaires</h1>
          <p class="text-xs text-gray-500 mt-1">
            Tableau de bord géographique des bénéficiaires par région et zone d'intervention.
          </p>
        </div>
      </div>

      <LoadingSpinner v-if="loading" message="Chargement des bénéficiaires et des zones..." />
      <AlertMessage v-if="error" type="error" :message="error" class="mb-4" />

      <!-- Cartes statistiques (en haut) -->
      <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div class="bg-white border border-slate-200 rounded-xl p-4 shadow-xs-sm">
          <p class="text-xs font-bold uppercase text-slate-900">Région</p>
          <p class="text-xl font-bold text-slate-900 mt-1">{{ selectedRegion || 'Cliquez sur une région' }}</p>
        </div>
        <div class="bg-white border border-slate-200 rounded-xl p-4 shadow-xs-sm">
          <p class="text-xs font-bold uppercase text-slate-900">Total Bénéficiaires</p>
          <p class="text-2xl font-bold text-or mt-1">{{ selectedRegion ? regionBeneficiairesCount : totalBeneficiairesCount }}</p>
        </div>
        <div class="bg-white border border-slate-200 rounded-xl p-4 shadow-xs-sm">
          <p class="text-xs font-bold uppercase text-slate-900">Zones</p>
          <p class="text-2xl font-bold text-slate-900 mt-1">{{ selectedRegion ? regionZones.length : zoneStore.zones.length }}</p>
        </div>
        <div class="bg-white border border-slate-200 rounded-xl p-4 shadow-xs-sm">
          <p class="text-xs font-bold uppercase text-slate-900">Campagnes Actives</p>
          <p class="text-2xl font-bold text-or mt-1">{{ activeCampaignsCount }}</p>
        </div>
      </div>

      <!-- Carte + Fiche à côté -->
      <div class="flex flex-col lg:flex-row gap-6">
        <!-- Carte -->
        <div class="flex-1 min-w-0">
          <div class="h-[calc(100vh-340px)] min-h-[420px] rounded-xl border border-slate-200/60 overflow-hidden">
            <CarteSenegal
              ref="carteRef"
              :geojson="geoJsonSenegal"
              :zones="zonesPourCarte"
              mode="readonly"
              @region-selected="onRegionSelected"
            />
          </div>
        </div>

        <!-- Fiche à droite -->
        <div class="w-full lg:w-[340px] flex-shrink-0 overflow-y-auto">
          <!-- Top 5 zones critiques -->
          <div v-if="topZones.length > 0" class="bg-white border border-slate-200 rounded-xl p-4 shadow-xs-sm mb-4">
            <h3 class="font-semibold text-slate-900 mb-3">Top zones prioritaires</h3>
            <div class="space-y-2">
              <div
                v-for="(zone, index) in topZones"
                :key="zone.id || index"
                class="flex justify-between items-center px-3 py-2 rounded-lg"
                :class="(zone.scoreIA || 0) >= 80 ? 'bg-red-50 border border-red-100' : (zone.scoreIA || 0) >= 50 ? 'bg-orange-50 border border-orange-100' : 'bg-or/10 border border-or/30'"
              >
                <div class="flex items-center gap-2">
                  <span class="text-xs font-bold text-gray-400 w-4">{{ index + 1 }}</span>
                  <span class="text-sm font-semibold text-slate-900">{{ zone.nom }}</span>
                </div>
                <div class="flex items-center gap-2">
                  <span class="text-xs text-gray-600">{{ zone.beneficiairesCount }} bénéf.</span>
                  <span
                    class="px-2 py-0.5 rounded text-xs font-semibold"
                    :class="(zone.scoreIA || 0) >= 80 ? 'bg-red-100 text-red-700' : (zone.scoreIA || 0) >= 50 ? 'bg-orange-100 text-orange-700' : 'bg-or/10 text-or'"
                  >
                    {{ (zone.scoreIA || 0) >= 80 ? 'Critique' : (zone.scoreIA || 0) >= 50 ? 'Élevé' : 'Normal' }}
                  </span>
                </div>
              </div>
            </div>
          </div>

          <!-- Bouton Évaluer -->
          <button
            @click="showEvalPanel = !showEvalPanel"
            :disabled="!selectedRegion"
            class="w-full h-11 bg-bleu-nuit text-white rounded-xl text-sm font-semibold hover:bg-[#01111eff] disabled:opacity-50 transition flex items-center justify-center gap-2 mb-4"
          >
            <svg class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"/>
            </svg>
            Évaluer
          </button>

          <!-- Panneau IA -->
          <div v-if="showEvalPanel" class="bg-bleu-nuit text-white rounded-xl p-4 shadow-xs-sm">
            <h4 class="font-semibold mb-3 flex items-center gap-2">
              <div class="w-2 h-2 bg-emerald-400 rounded-full"></div>
              Analyse IA - {{ selectedRegion || 'Toutes les régions' }}
            </h4>
            <p class="text-sm text-gray-300 leading-relaxed">
              {{ evalText }}
            </p>
            <div class="mt-3 pt-3 border-t border-gray-700">
              <p class="text-xs text-gray-400">Synthèse générée à partir des données terrain réelles.</p>
            </div>
          </div>

          <!-- Carte IA de priorisation -->
          <IAPrioritisationCard
            :campagneId="firstCampaignId"
            :projetId="firstProjetId"
            :zones="zonesForIA"
            class="mt-4"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from "vue"
import CarteSenegal from "@/modules/chef-projet/components/zones/CarteSenegal.vue"
import LoadingSpinner from "@/components/ui/LoadingSpinner.vue"
import AlertMessage from "@/components/ui/AlertMessage.vue"
import IAPrioritisationCard from "@/modules/gerant/components/ia/IAPrioritisationCard.vue"
import geoJsonRaw from "@/data/senegal-regions.geojson?raw"
import { useBeneficiaryStore } from "@/stores/beneficiary.js"
import { useZoneStore } from "@/stores/zone.js"
import { useCampaignStore } from "@/stores/campaign.js"

const beneficiaryStore = useBeneficiaryStore()
const zoneStore = useZoneStore()
const campaignStore = useCampaignStore()

const geoJsonSenegal = JSON.parse(geoJsonRaw)
const carteRef = ref(null)
const selectedRegion = ref("")
const showEvalPanel = ref(false)
const loading = ref(false)
const error = ref(null)

onMounted(async () => {
  loading.value = true
  error.value = null
  try {
    await Promise.allSettled([
      beneficiaryStore.fetchBeneficiaries(),
      zoneStore.fetchZones(),
      campaignStore.fetchCampaigns(),
    ])
  } catch (err) {
    error.value = "Erreur lors du chargement des données."
  } finally {
    loading.value = false
  }
})

const totalBeneficiariesCount = computed(() => {
  return beneficiaryStore.beneficiaries.length
})

const activeCampaignsCount = computed(() => {
  return campaignStore.activeCampaigns.length || campaignStore.campaigns.length
})

const regionZones = computed(() => {
  if (!selectedRegion.value) return zoneStore.zones
  return zoneStore.zones.filter((z) => (z.region || "").toLowerCase() === selectedRegion.value.toLowerCase())
})

const regionBeneficiairesCount = computed(() => {
  if (!selectedRegion.value) return beneficiaryStore.beneficiaries.length
  const zoneIds = new Set(regionZones.value.map((z) => z.id))
  return beneficiaryStore.beneficiaries.filter((b) => zoneIds.has(b.zone?.id || b.zone_id)).length
})

const zonesPourCarte = computed(() => {
  return zoneStore.zones.map((z) => {
    const benefCount = beneficiaryStore.beneficiaries.filter(
      (b) => (b.zone?.id || b.zone_id) === z.id
    ).length

    return {
      id: z.id,
      nom: z.nom,
      region: z.region,
      departement: z.departement || z.nom,
      latitude: z.latitude,
      longitude: z.longitude,
      rayon: z.rayon_km ? z.rayon_km * 1000 : (z.rayon || 2000),
      statut: z.statut === "ACTIF" ? "Actif" : "Inactif",
      beneficiairesCount: benefCount,
    }
  })
})

const topZones = computed(() => {
  const list = regionZones.value.map((z) => {
    const benefs = beneficiaryStore.beneficiaries.filter((b) => (b.zone?.id || b.zone_id) === z.id)
    const avgScore = benefs.length
      ? Math.round(benefs.reduce((acc, b) => acc + (Number.isFinite(b.ai_score) ? b.ai_score : 0), 0) / benefs.length)
      : 0
    return {
      ...z,
      beneficiairesCount: benefs.length,
      scoreIA: avgScore,
    }
  })

  return list
    .sort((a, b) => b.scoreIA - a.scoreIA || b.beneficiairesCount - a.beneficiairesCount)
    .slice(0, 5)
})

const onRegionSelected = (payload) => {
  selectedRegion.value = payload.region
  showEvalPanel.value = false
}

const evalText = computed(() => {
  if (!selectedRegion.value) return "Sélectionnez une région pour générer une analyse IA."
  const totalBenefs = regionBeneficiairesCount.value
  const zoneCount = regionZones.value.length
  const top = topZones.value[0]

  let text = `Région ${selectedRegion.value} : ${totalBenefs} bénéficiaire(s) recensé(s) dans ${zoneCount} zone(s). `
  if (top && top.beneficiairesCount > 0) {
    text += `La zone avec la plus grande affluence est ${top.nom} avec ${top.beneficiairesCount} bénéficiaire(s). `
  } else {
    text += "Aucun regroupement critique identifié à ce stade. "
  }
  text += "Le déploiement des campagnes et la distribution de secours peuvent se poursuivre selon le planning établi."
  return text
})

const firstCampaignId = computed(() => campaignStore.campaigns?.[0]?.id || null)
const firstProjetId = computed(() => {
  const first = campaignStore.campaigns?.[0]
  return first?.projet?.id || first?.projet_id || null
})
const zonesForIA = computed(() =>
  zoneStore.zones.map((z) => ({
    nom: z.nom,
    urgence: "Moyenne",
    score_total: 0,
    beneficiaires_prioritaires: 0,
    top5: [],
  }))
)
</script>

