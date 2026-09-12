<template>
  <div class="p-6 space-y-6 bg-white min-h-screen">
    <!-- En-tête -->
    <div class="flex justify-between items-center border-b border-slate-200 pb-4">
      <div>
        <h1 class="text-3xl font-bold text-amber-800">Créer une zone</h1>
        <p class="text-xs text-gray-500 mt-1">
          Sélectionnez une région sur la carte, puis un point pour définir une zone.
        </p>
      </div>

      <div class="flex gap-3">

        <BoutonSecondary to="/chef-projet/zones">
          <List :size="18" />
          Liste des zones
        </BoutonSecondary>
      </div>
    </div>

    <!-- Carte + Formulaire -->
    <div class="h-[calc(100vh-180px)] flex gap-6">
      <div class="flex-1 rounded-xl border border-slate-200/60 overflow-hidden">
        <CarteSenegal
          :geojson="geoJsonSenegal"
          :form="form"
          :zones="zonesMock"
          mode="creation"
          @region-selected="onRegionSelected"
          @map-click="onMapClick"
          @submit="onSubmit"
        />
      </div>

      <div class="w-96 bg-white border-l border-slate-200 p-6 overflow-y-auto rounded-r-xl">
        <h2 class="text-xl font-bold text-amber-800 mb-1">Formulaire de zone</h2>
        <p class="text-xs text-gray-500 mb-6">
          Remplissez les informations de la zone.
        </p>

        <FormulaireZone
          mode="creation"
          :initial-data="form"
          @submit="onSubmit"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { reactive } from "vue"
import { MapPinned, List } from "lucide-vue-next"
import BoutonSecondary from "@/components/ui/BoutonSecondary.vue"
import CarteSenegal from "@/modules/chef-projet/components/zones/CarteSenegal.vue"
import FormulaireZone from "@/modules/chef-projet/components/zones/FormulaireZone.vue"
import { zonesMock } from "@/data/zonesMock.js"
import geoJsonSenegalRaw from "@/data/senegal-regions.geojson?raw"

const geoJsonSenegal = JSON.parse(geoJsonSenegalRaw)

const form = reactive({
  region: "",
  departement: "",
  nom: "",
  rayon: "",
  statut: "Actif",
  latitude: null,
  longitude: null,
  submitDone: false,
})

const onRegionSelected = ({ region, departement }) => {
  form.region = region
  form.departement = departement
}

const onMapClick = ({ latitude, longitude }) => {
  form.latitude = latitude
  form.longitude = longitude
}

const onSubmit = (data) => {
  const nouvelleZone = {
    id: Date.now(),
    ...data,
    dateCreation: new Date().toISOString().split("T")[0],
  }

  zonesMock.value.push(nouvelleZone)

  form.submitDone = true
  setTimeout(() => {
    form.submitDone = false
  }, 100)

  console.log("Nouvelle zone:", nouvelleZone)
  alert("Zone créée avec succès !")
}
</script>
