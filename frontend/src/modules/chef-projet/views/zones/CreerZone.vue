<template>
  <div class="p-6 space-y-6 bg-white min-h-screen">
    <!-- En-tête -->
    <div class="flex justify-between items-center pb-4">
      <div>
        <h1 class="text-3xl font-bold text-or">Créer une zone</h1>
        <p class="text-xs text-gray-500 mt-1">
          Sélectionnez une région sur la carte, puis cliquez sur le centre de la zone.
        </p>
      </div>

      <div class="flex gap-3">
        <BoutonSecondary to="/chef-projet/zones">
          <List :size="18" />
          Liste des zones
        </BoutonSecondary>
      </div>
    </div>

    <AlertMessage v-if="feedback.message" :type="feedback.type" :message="feedback.message" class="mb-4" />

    <!-- Carte + Formulaire -->
    <div class="h-[calc(100vh-220px)] flex flex-col lg:flex-row gap-6">
      <div class="flex-1 rounded-xl border border-slate-200/60 overflow-hidden min-h-[400px]">
        <CarteSenegal
          :geojson="geoJsonSenegal"
          :form="form"
          :zones="zoneStore.zones"
          mode="creation"
          @region-selected="onRegionSelected"
          @map-click="onMapClick"
          @submit="onSubmit"
        />
      </div>

      <div class="w-full lg:w-96 bg-white border border-slate-200 p-6 overflow-y-auto rounded-xl shadow-xs-sm">
        <h2 class="text-xl font-bold text-or mb-1">Formulaire de zone</h2>
        <p class="text-xs text-gray-500 mb-6">
          Remplissez les informations de la zone après avoir cliqué sur la carte.
        </p>

        <FormulaireZone
          mode="creation"
          :initial-data="form"
          @submit="onSubmit"
        />
      </div>
    </div>
  </div>

  <OperationalOrbitalIA />
</template>

<script setup>
import { reactive, onMounted } from "vue"
import { useRouter } from "vue-router"
import { List } from "lucide-vue-next"
import BoutonSecondary from "@/components/ui/BoutonSecondary.vue"
import AlertMessage from "@/components/ui/AlertMessage.vue"
import OperationalOrbitalIA from "@/components/ia/OperationalOrbitalIA.vue"
import CarteSenegal from "@/modules/chef-projet/components/zones/CarteSenegal.vue"
import FormulaireZone from "@/modules/chef-projet/components/zones/FormulaireZone.vue"
import { useZoneStore } from "@/stores/zone.js"
import geoJsonSenegalRaw from "@/data/senegal-regions.geojson?raw"

const router = useRouter()
const zoneStore = useZoneStore()
const geoJsonSenegal = JSON.parse(geoJsonSenegalRaw)

const feedback = reactive({ type: "success", message: "" })

const form = reactive({
  region: "",
  departement: "",
  nom: "",
  description: "",
  rayon: 1000,
  statut: true,
  latitude: null,
  longitude: null,
  submitDone: false,
})

onMounted(async () => {
  try {
    await zoneStore.fetchZones()
  } catch (e) {}
})

const onRegionSelected = ({ region, departement }) => {
  form.region = region
  form.departement = departement
}

const onMapClick = ({ latitude, longitude }) => {
  form.latitude = latitude
  form.longitude = longitude
}

const onSubmit = async (data) => {
  feedback.message = ""

  if (!data.latitude || !data.longitude) {
    feedback.type = "error"
    feedback.message = "Veuillez cliquer sur la carte pour définir le centre de la zone (latitude/longitude)."
    return
  }

  try {
    await zoneStore.createZone({
      nom: data.nom,
      region: data.region,
      departement: data.departement,
      latitude: Number(parseFloat(data.latitude).toFixed(7)),
      longitude: Number(parseFloat(data.longitude).toFixed(7)),
      rayon: Number(data.rayon),
      statut: true,
    })

    feedback.type = "success"
    feedback.message = "Zone créée avec succès !"
    setTimeout(() => {
      router.push("/chef-projet/zones")
    }, 900)
  } catch (err) {
    feedback.type = "error"
    feedback.message = zoneStore.error || "Erreur lors de la création de la zone."
  }
}
</script>

