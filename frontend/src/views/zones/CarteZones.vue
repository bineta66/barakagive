<template>
  <div class="p-6 space-y-6 bg-white min-h-screen">
    <!-- En-tête -->
    <div class="flex justify-between items-center border-b border-slate-200 pb-4">
      <div>
        <h1 class="text-3xl font-bold text-amber-800">Zones d'intervention</h1>
        <p class="text-xs text-gray-500 mt-1">
          Consultez les zones enregistrées sur la carte du Sénégal.
        </p>
      </div>

      <div class="flex gap-3">
        <RouterLink
          to="/zones/liste"
          class="border border-sky-900 text-sky-900 px-4 py-2 rounded-lg text-sm font-semibold flex items-center gap-2"
        >
          <List :size="18" />
          Liste des zones
        </RouterLink>

        <RouterLink
          to="/zones/creer"
          class="bg-slate-900 hover:bg-slate-800 text-white px-4 py-2 rounded-lg text-sm font-semibold flex items-center gap-2"
        >
          <Plus :size="18" />
          Nouvelle zone
        </RouterLink>
      </div>
    </div>

    <!-- Carte -->
    <div class="h-[calc(100vh-180px)] rounded-xl border border-slate-200/60 overflow-hidden">
      <CarteSenegal
        :geojson="geoJsonSenegal"
        :zones="zonesMock"
        mode="readonly"
      />
    </div>
  </div>
</template>

<script setup>
import { Plus, List } from "lucide-vue-next"
import CarteSenegal from "@/components/zones/CarteSenegal.vue"
import { zonesMock } from "@/data/zonesMock.js"
import geoJsonSenegalRaw from "@/data/senegal-regions.geojson?raw"

const geoJsonSenegal = JSON.parse(geoJsonSenegalRaw)

</script>
