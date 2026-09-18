<template>
  <div class="p-6 space-y-6 bg-white min-h-screen">
    <!-- En-tête -->
    <div class="flex justify-between items-center pb-4">
      <div>
        <h1 class="text-3xl font-bold text-or">Carte des zones</h1>
        <p class="text-xs text-gray-500 mt-1">
          Consultez les zones enregistrées sur la carte interactive du Sénégal.
        </p>
      </div>

      <div class="flex gap-3">
        <BoutonSecondary to="/chef-projet/zones">
          <List :size="18" />
          Liste des zones
        </BoutonSecondary>

        <BoutonPrimary to="/chef-projet/zones/creer">
          <Plus :size="18" />
          Nouvelle zone
        </BoutonPrimary>
      </div>
    </div>

    <LoadingSpinner v-if="zoneStore.loading && !zoneStore.zones.length" message="Chargement de la carte..." />

    <div class="grid lg:grid-cols-3 gap-6">
      <!-- Carte (2/3) -->
      <div class="lg:col-span-2 h-[calc(100vh-180px)] rounded-xl border border-slate-200/60 overflow-hidden">
        <CarteSenegal
          :geojson="geoJsonSenegal"
          :zones="zoneStore.zones"
          mode="readonly"
          @region-selected="onRegionSelected"
        />
      </div>

      <!-- Zone Analysis Panel (1/3) -->
      <div class="lg:col-span-1">
        <ZoneAnalysisPanel
          :selected-region="selectedRegion"
          @zone-selected="goToZoneDetail"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from "vue"
import { List, Plus } from "lucide-vue-next"
import { useRouter } from "vue-router"
import BoutonPrimary from "@/components/ui/BoutonPrimary.vue"
import BoutonSecondary from "@/components/ui/BoutonSecondary.vue"
import LoadingSpinner from "@/components/ui/LoadingSpinner.vue"
import CarteSenegal from "@/modules/chef-projet/components/zones/CarteSenegal.vue"
import ZoneAnalysisPanel from "@/modules/chef-projet/components/zones/ZoneAnalysisPanel.vue"
import { useZoneStore } from "@/stores/zone.js"
import geoJsonSenegalRaw from "@/data/senegal-regions.geojson?raw"

const router = useRouter()
const zoneStore = useZoneStore()
const geoJsonSenegal = JSON.parse(geoJsonSenegalRaw)

const selectedRegion = ref("")

const onRegionSelected = (data) => {
  selectedRegion.value = data.region
}

const goToZoneDetail = (zoneId) => {
  router.push(`/chef-projet/zones/analyse/${zoneId}`)
}

onMounted(async () => {
  try {
    await zoneStore.fetchZones()
  } catch (e) {}
})
</script>

