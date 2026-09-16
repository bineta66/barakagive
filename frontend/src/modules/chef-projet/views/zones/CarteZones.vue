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

    <!-- Carte -->
    <div class="h-[calc(100vh-180px)] rounded-xl border border-slate-200/60 overflow-hidden">
      <CarteSenegal
        :geojson="geoJsonSenegal"
        :zones="zoneStore.zones"
        mode="readonly"
      />
    </div>
  </div>
</template>

<script setup>
import { onMounted } from "vue"
import { List, Plus } from "lucide-vue-next"
import BoutonPrimary from "@/components/ui/BoutonPrimary.vue"
import BoutonSecondary from "@/components/ui/BoutonSecondary.vue"
import LoadingSpinner from "@/components/ui/LoadingSpinner.vue"
import CarteSenegal from "@/modules/chef-projet/components/zones/CarteSenegal.vue"
import { useZoneStore } from "@/stores/zone.js"
import geoJsonSenegalRaw from "@/data/senegal-regions.geojson?raw"

const zoneStore = useZoneStore()
const geoJsonSenegal = JSON.parse(geoJsonSenegalRaw)

onMounted(async () => {
  try {
    await zoneStore.fetchZones()
  } catch (e) {}
})
</script>

