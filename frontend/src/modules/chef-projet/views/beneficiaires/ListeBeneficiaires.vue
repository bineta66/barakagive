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
        <div class="w-full lg:w-[360px] flex-shrink-0 overflow-y-auto space-y-4">
          <div v-if="topZones.length" class="bg-white border border-slate-200 rounded-xl p-4 shadow-xs-sm">
            <h3 class="font-semibold text-slate-900 mb-2">Top 5 zones prioritaires</h3>
            <p class="text-xs text-gray-500 mb-3">Classement par score total et bénéficiaires prioritaires.</p>
            <div class="space-y-2">
              <div
                v-for="(zone, index) in topZones"
                :key="zone.nom || index"
                class="rounded-lg border border-slate-100 p-3"
                :class="(zone.urgenceClass || 'bg-or/10')"
              >
                <div class="flex items-center justify-between mb-1">
                  <div class="flex items-center gap-2">
                    <span class="text-xs font-bold text-gray-400 w-4">{{ index + 1 }}</span>
                    <span class="text-sm font-semibold text-slate-900">{{ zone.nom }}</span>
                  </div>
                  <span class="px-2 py-0.5 rounded text-xs font-semibold" :class="zone.urgenceBadge">
                    {{ zone.urgence }}
                  </span>
                </div>
                <div class="flex items-center justify-between text-xs text-gray-600 mb-1">
                  <span>Score total : <span class="font-semibold">{{ zone.score_total }}</span></span>
                  <span>{{ zone.beneficiairesCount }} bénéf.</span>
                </div>
                <button
                  type="button"
                  class="text-xs font-semibold text-bleu-nuit hover:underline"
                  @click="ouvrirZone(zone)"
                >
                  Voir plus
                </button>
              </div>
            </div>
          </div>

          <div v-else class="bg-white border border-slate-200 rounded-xl p-4 shadow-xs-sm">
            <p class="text-xs text-gray-500">Aucune zone prioritaire identifiée pour le moment.</p>
          </div>

          <div v-if="selectedZone" class="bg-white border border-slate-200 rounded-xl p-4 shadow-xs-sm">
            <div class="flex items-center justify-between mb-2">
              <h3 class="font-semibold text-slate-900">Bénéficiaires prioritaires - {{ selectedZone.nom }}</h3>
              <button type="button" class="text-xs text-gray-500 hover:text-slate-900" @click="fermerZone">Fermer</button>
            </div>
            <p class="text-xs text-gray-500 mb-3">Top 5 bénéficiaires les plus urgents, avec les raisons issues des critères et réponses.</p>
            <div v-if="selectedZone.beneficiaires?.length" class="space-y-2">
              <div v-for="benef in selectedZone.beneficiaires" :key="benef.id || benef.nom" class="rounded-lg border border-slate-100 p-2">
                <div class="flex items-center justify-between mb-1">
                  <span class="text-sm font-semibold text-slate-900">{{ benef.nom }}</span>
                  <span class="px-2 py-0.5 rounded text-xs font-semibold" :class="benef.score >= 80 ? 'bg-red-100 text-red-700' : benef.score >= 50 ? 'bg-orange-100 text-orange-700' : 'bg-or/10 text-or'">
                    {{ benef.score }}
                  </span>
                </div>
                <div v-if="benef.raisons?.length" class="text-xs text-gray-600">
                  <span class="font-semibold">Pourquoi :</span>
                  <ul class="list-disc list-inside mt-1 space-y-1">
                    <li v-for="(raison, idx) in benef.raisons" :key="idx">{{ raison }}</li>
                  </ul>
                </div>
              </div>
            </div>
            <p v-else class="text-xs text-gray-500">Aucun bénéficiaire prioritaire à afficher pour cette zone.</p>
          </div>
        </div>
      </div>
    </div>
  </div>

  <OperationalOrbitalIA />
</template>

<script setup>
import { ref, computed, onMounted } from "vue"
import CarteSenegal from "@/modules/chef-projet/components/zones/CarteSenegal.vue"
import LoadingSpinner from "@/components/ui/LoadingSpinner.vue"
import AlertMessage from "@/components/ui/AlertMessage.vue"
import OperationalOrbitalIA from "@/components/ia/OperationalOrbitalIA.vue"
import geoJsonRaw from "@/data/senegal-regions.geojson?raw"
import api from "@/services/api.js"
import { useBeneficiaryStore } from "@/stores/beneficiary.js"
import { useZoneStore } from "@/stores/zone.js"
import { useCampaignStore } from "@/stores/campaign.js"

const beneficiaryStore = useBeneficiaryStore()
const zoneStore = useZoneStore()
const campaignStore = useCampaignStore()

const geoJsonSenegal = JSON.parse(geoJsonRaw)
const carteRef = ref(null)
const selectedRegion = ref("")
const loading = ref(false)
const error = ref(null)
const zoneRanking = ref([])

onMounted(async () => {
  loading.value = true
  error.value = null
  try {
    await Promise.allSettled([
      beneficiaryStore.fetchBeneficiaries(),
      zoneStore.fetchZones(),
      campaignStore.fetchCampaigns(),
    ])

    const campaignId = campaignStore.campaigns?.[0]?.id
    if (campaignId) {
      try {
        const response = await api.get(`/api/beneficiaries/zone-ranking/`, {
          params: { campaign_id: campaignId },
        })
        zoneRanking.value = response.data || []
      } catch {
        zoneRanking.value = []
      }
    }
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

const onRegionSelected = (payload) => {
  selectedRegion.value = payload.region || ""
}

const urgencePourZone = (zone) => {
  const score = zone.score_total || 0
  const prioritaires = zone.beneficiaires_prioritaires || 0
  if (score >= 200 || prioritaires >= 20) return { urgence: "Très élevée", classe: "bg-red-50", badge: "bg-red-100 text-red-700" }
  if (score >= 100 || prioritaires >= 10) return { urgence: "Élevée", classe: "bg-orange-50", badge: "bg-orange-100 text-orange-700" }
  if (score >= 50 || prioritaires >= 5) return { urgence: "Moyenne", classe: "bg-or/10", badge: "bg-or/10 text-or" }
  return { urgence: "Faible", classe: "bg-gray-50", badge: "bg-gray-100 text-gray-700" }
}

const topZones = computed(() => {
  const ranking = (zoneRanking.value || []).slice(0, 5)
  return ranking.map((zone) => {
    const info = urgencePourZone(zone)
    return {
      nom: zone.nom,
      score_total: zone.score_total || 0,
      beneficiairesCount: zone.beneficiaires_prioritaires || 0,
      urgence: info.urgence,
      urgenceClass: info.classe,
      urgenceBadge: info.badge,
      beneficiaires: (zone.top5 || []).map((b) => ({
        id: b.id,
        nom: b.nom,
        score: b.score || 0,
        raisons: b.raisons || [],
      })),
    }
  })
})

const selectedZone = ref(null)

const ouvrirZone = (zone) => {
  selectedZone.value = zone
}

const fermerZone = () => {
  selectedZone.value = null
}
</script>

