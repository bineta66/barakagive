<template>
  <div class="p-6 space-y-6 bg-white min-h-screen">
    <!-- En-tête -->
    <div class="flex justify-between items-center pb-4">
      <div>
        <h1 class="text-3xl font-bold text-or">Modifier la zone</h1>
        <p class="text-xs text-gray-500 mt-1">
          Modifiez les informations et l'emplacement de la zone.
        </p>
      </div>

      <div class="flex gap-3">
        <BoutonSecondary to="/chef-projet/zones">
          <List :size="18" />
          Liste des zones
        </BoutonSecondary>
      </div>
    </div>

    <LoadingSpinner v-if="loading" message="Chargement de la zone..." />
    <AlertMessage v-if="feedback.message" :type="feedback.type" :message="feedback.message" class="mb-4" />

    <!-- Carte + Formulaire -->
    <div v-if="!loading && zone" class="h-[calc(100vh-220px)] flex flex-col lg:flex-row gap-6">
      <div class="flex-1 rounded-xl border border-slate-200/60 overflow-hidden min-h-[400px]">
        <CarteSenegal
          :geojson="geoJsonSenegal"
          :form="form"
          :zones="[zone]"
          mode="creation"
          @region-selected="onRegionSelected"
          @map-click="onMapClick"
          @submit="onSubmit"
        />
      </div>

      <div class="w-full lg:w-96 bg-white border border-slate-200 p-6 overflow-y-auto rounded-xl shadow-xs-sm">
        <h2 class="text-xl font-bold text-or mb-1">Modifier la zone</h2>
        <p class="text-xs text-gray-500 mb-6">
          Modifiez les informations de la zone.
        </p>

        <FormulaireZone
          mode="modification"
          :initial-data="form"
          @submit="onSubmit"
        />
      </div>
    </div>
  </div>

  <OperationalOrbitalIA />
</template>

<script setup>
import { reactive, ref, onMounted } from "vue"
import { useRoute, useRouter } from "vue-router"
import { List } from "lucide-vue-next"
import BoutonSecondary from "@/components/ui/BoutonSecondary.vue"
import LoadingSpinner from "@/components/ui/LoadingSpinner.vue"
import AlertMessage from "@/components/ui/AlertMessage.vue"
import OperationalOrbitalIA from "@/components/ia/OperationalOrbitalIA.vue"
import CarteSenegal from "@/modules/chef-projet/components/zones/CarteSenegal.vue"
import FormulaireZone from "@/modules/chef-projet/components/zones/FormulaireZone.vue"
import { useZoneStore } from "@/stores/zone.js"
import geoJsonSenegalRaw from "@/data/senegal-regions.geojson?raw"

const route = useRoute()
const router = useRouter()
const zoneStore = useZoneStore()
const geoJsonSenegal = JSON.parse(geoJsonSenegalRaw)

const loading = ref(true)
const feedback = reactive({ type: "success", message: "" })
const zone = ref(null)

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
    loading.value = true
    try {
      const data = await zoneStore.fetchZone(route.params.id)
      zone.value = data
      form.nom = data.nom || ""
      form.description = data.description || ""
      form.region = data.region || ""
      form.departement = data.departement || ""
      form.latitude = data.latitude
      form.longitude = data.longitude
      form.rayon = data.rayon || 1000
      form.statut = data.statut === false ? false : true
    } catch (err) {
      feedback.type = "error"
      feedback.message = "Erreur lors du chargement de la zone."
    } finally {
      loading.value = false
    }
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
    try {
      await zoneStore.updateZone(route.params.id, {
        nom: data.nom,
        region: data.region,
        departement: data.departement,
        latitude: Number(parseFloat(data.latitude).toFixed(7)),
        longitude: Number(parseFloat(data.longitude).toFixed(7)),
        rayon: Number(data.rayon),
        statut: Boolean(data.statut),
      })

      feedback.type = "success"
      feedback.message = "Zone mise à jour avec succès !"
      setTimeout(() => {
        router.push("/chef-projet/zones")
      }, 900)
    } catch (err) {
      feedback.type = "error"
      feedback.message = zoneStore.error || "Erreur lors de la modification de la zone."
    }
  }
</script>

