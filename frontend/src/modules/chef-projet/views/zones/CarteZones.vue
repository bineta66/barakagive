<template>
  <div class="p-6 space-y-6 bg-white min-h-screen">
    <!-- En-tÃªte -->
    <div class="flex justify-between items-center  pb-4">
      <div>
        <h1 class="text-3xl font-bold text-or">Zones d'intervention</h1>
        <p class="text-xs text-gray-500 mt-1">
          Consultez les zones enregistrÃ©es sur la carte du SÃ©nÃ©gal.
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
import { List, Plus } from "lucide-vue-next"
import BoutonPrimary from "@/components/ui/BoutonPrimary.vue"
import BoutonSecondary from "@/components/ui/BoutonSecondary.vue"
import CarteSenegal from "@/modules/chef-projet/components/zones/CarteSenegal.vue"
import { zonesMock } from "@/data/zonesMock.js"
import geoJsonSenegalRaw from "@/data/senegal-regions.geojson?raw"

const geoJsonSenegal = JSON.parse(geoJsonSenegalRaw)

</script>

