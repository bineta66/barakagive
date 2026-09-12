<template>
  <div class="p-6 bg-white min-h-screen">
    <div class="space-y-4">
      <!-- En-tête -->
      <div class="flex justify-between items-center border-b border-slate-200 pb-4">
        <div>
          <h1 class="text-3xl font-bold text-yellow-800">Bénéficiaires</h1>
          <p class="text-xs text-gray-500 mt-1">
            Tableau de bord géographique des bénéficiaires par région et zone d'intervention.
          </p>
        </div>
      </div>

      <!-- Cartes statistiques (en haut) -->
      <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div class="bg-white border border-slate-200 rounded-xl p-4 shadow-sm">
          <p class="text-xs font-bold uppercase text-slate-900">Région</p>
          <p class="text-xl font-bold text-slate-900 mt-1">{{ selectedRegion || 'Cliquez sur une région' }}</p>
        </div>
        <div class="bg-white border border-slate-200 rounded-xl p-4 shadow-sm">
          <p class="text-xs font-bold uppercase text-slate-900">Total Bénéficiaires</p>
          <p class="text-2xl font-bold text-yellow-800 mt-1">{{ selectedRegion ? regionStats?.totalBeneficiaires : '—' }}</p>
        </div>
        <div class="bg-white border border-slate-200 rounded-xl p-4 shadow-sm">
          <p class="text-xs font-bold uppercase text-slate-900">Zones</p>
          <p class="text-2xl font-bold text-slate-900 mt-1">{{ selectedRegion ? displayedZones.length : '—' }}</p>
        </div>
        <div class="bg-white border border-slate-200 rounded-xl p-4 shadow-sm">
          <p class="text-xs font-bold uppercase text-slate-900">Campagnes Actives</p>
          <p class="text-2xl font-bold text-yellow-800 mt-1">{{ selectedRegion ? regionStats?.campagnesActives : '—' }}</p>
        </div>
      </div>

      <!-- Carte + Fiche à côté -->
      <div class="flex gap-6">
        <!-- Carte -->
        <div class="flex-1 min-w-0">
          <div class="h-[calc(100vh-340px)] rounded-xl border border-slate-200/60 overflow-hidden">
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
        <div class="w-[340px] flex-shrink-0 overflow-y-auto">
          <!-- Top 5 zones critiques -->
          <div v-if="topZones.length > 0" class="bg-white border border-slate-200 rounded-xl p-4 shadow-sm mb-4">
            <h3 class="font-semibold text-slate-900 mb-3">Top 5 zones critiques</h3>
            <div class="space-y-2">
              <div
                v-for="(zone, index) in topZones"
                :key="zone.nom"
                class="flex justify-between items-center px-3 py-2 rounded-lg"
                :class="zone.scoreIA >= 80 ? 'bg-red-50 border border-red-100' : zone.scoreIA >= 60 ? 'bg-orange-50 border border-orange-100' : 'bg-yellow-50 border border-yellow-100'"
              >
                <div class="flex items-center gap-2">
                  <span class="text-xs font-bold text-gray-400 w-4">{{ index + 1 }}</span>
                  <span class="text-sm font-semibold text-slate-900">{{ zone.nom }}</span>
                </div>
                <div class="flex items-center gap-2">
                  <span class="text-xs text-gray-600">{{ zone.beneficiaires }} bénéf.</span>
                  <span
                    class="px-2 py-0.5 rounded text-xs font-semibold"
                    :class="zone.scoreIA >= 80 ? 'bg-red-100 text-red-700' : zone.scoreIA >= 60 ? 'bg-orange-100 text-orange-700' : 'bg-yellow-100 text-yellow-700'"
                  >
                    {{ zone.scoreIA >= 80 ? 'Critique' : zone.scoreIA >= 60 ? 'Élevé' : 'Moyen' }}
                  </span>
                </div>
              </div>
            </div>
          </div>

          <!-- Bouton Évaluer -->
          <button
            @click="showEvalPanel = !showEvalPanel"
            :disabled="!selectedRegion"
            class="w-full h-11 bg-slate-900 text-white rounded-xl text-sm font-semibold hover:bg-slate-800 disabled:opacity-50 transition flex items-center justify-center gap-2 mb-4"
          >
            <svg class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"/>
            </svg>
            Évaluer
          </button>

          <!-- Panneau IA -->
          <div v-if="showEvalPanel" class="bg-slate-900 text-white rounded-xl p-4 shadow-lg">
            <h4 class="font-semibold mb-3 flex items-center gap-2">
              <div class="w-2 h-2 bg-emerald-400 rounded-full"></div>
              Analyse IA — {{ selectedRegion || 'Toutes les régions' }}
            </h4>
            <p class="text-sm text-gray-300 leading-relaxed">
              {{ evalText }}
            </p>
            <div class="mt-3 pt-3 border-t border-gray-700">
              <p class="text-xs text-gray-400">Justification générée automatiquement à partir des données régionales.</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from "vue"
import CarteSenegal from "@/modules/chef-projet/components/zones/CarteSenegal.vue"
import geoJsonRaw from "@/data/senegal-regions.geojson?raw"
import { beneficiairesZonesMock, syntheseRegionMock } from "@/data/beneficiairesZonesMock.js"

const geoJsonSenegal = JSON.parse(geoJsonRaw)
const carteRef = ref(null)
const selectedRegion = ref("")
const displayedZones = ref([])
const showEvalPanel = ref(false)

const zonesPourCarte = computed(() => {
  const zoneList = []
  let id = 1
  beneficiairesZonesMock.forEach((region) => {
    region.zones.forEach((zone) => {
      zoneList.push({
        id: `${region.region}-${id}`,
        nom: zone.nom,
        region: region.region,
        departement: zone.nom,
        latitude: zone.latitude,
        longitude: zone.longitude,
        rayon: Math.max(zone.beneficiaires * 50, 2000),
        statut: zone.scoreIA >= 80 ? "Critique" : zone.scoreIA >= 60 ? "Élevé" : "Moyen",
      })
      id++
    })
  })
  return zoneList
})

const onRegionSelected = (payload) => {
  selectedRegion.value = payload.region
  showEvalPanel.value = false

  const regionData = beneficiairesZonesMock.find((r) => r.region === payload.region)
  displayedZones.value = regionData ? regionData.zones : []
}

const regionStats = computed(() => {
  if (!selectedRegion.value) return null
  return syntheseRegionMock[selectedRegion.value] || {
    totalBeneficiaires: 0,
    campagnesActives: 0,
    projetPrincipal: "—",
    urgencesElevees: 0,
  }
})

const topZones = computed(() => {
  const regionData = beneficiairesZonesMock.find((r) => r.region === selectedRegion.value)
  if (!regionData) return []
  return [...regionData.zones]
    .sort((a, b) => b.scoreIA - a.scoreIA)
    .slice(0, 5)
})

const evalText = computed(() => {
  if (!selectedRegion.value) return "Sélectionnez une région pour générer une analyse IA."
  const stats = regionStats.value || {}
  const zones = topZones.value
  const topZone = zones[0]
  const zoneCount = beneficiairesZonesMock.find((r) => r.region === selectedRegion.value)?.zones.length || 0

  let text = `Région ${selectedRegion.value} : ${stats.totalBeneficiaires} bénéficiaires répartis dans ${zoneCount} zones. `
  if (topZone) {
    text += `La zone la plus critique est ${topZone.nom} avec ${topZone.beneficiaires} bénéficiaires et un score IA de ${topZone.scoreIA}. `
  }
  if (stats.urgencesElevees > 5) {
    text += "Le niveau d'urgence est élevé, nécessitant une intervention rapide. "
  } else {
    text += "Le niveau d'urgence est modéré. "
  }
  text += "La forte concentration de bénéficiaires dans les zones prioritaires, combinée à une couverture des campagnes insuffisante, justifie ce classement."
  return text
})
</script>
