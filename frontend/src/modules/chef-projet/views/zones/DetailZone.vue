<template>
  <div class="p-6 space-y-6 bg-white min-h-screen">
    <div class="flex justify-between items-center pb-4">
      <div>
        <h1 class="text-3xl font-bold text-or">Détail de la zone</h1>
        <p class="text-sm text-gray-600 mt-1">
          Informations complètes de la zone d'intervention.
        </p>
      </div>

      <div class="flex gap-3">
        <BoutonSecondary to="/chef-projet/zones">
          <List :size="18" />
          Liste des zones
        </BoutonSecondary>
        <BoutonSecondary :to="`/chef-projet/zones/modifier/${route.params.id}`">
          Modifier
        </BoutonSecondary>
      </div>
    </div>

    <LoadingSpinner v-if="loading" message="Chargement de la zone..." />
    <AlertMessage v-if="error" type="error" :message="error" class="mb-4" />

<CarteInfoZone v-if="zone && !loading" :zone="zone" />
  </div>

  <OperationalOrbitalIA />
</template>

<script setup>
import { ref, onMounted } from "vue"
import { useRoute } from "vue-router"
import { List } from "lucide-vue-next"
import BoutonSecondary from "@/components/ui/BoutonSecondary.vue"
import LoadingSpinner from "@/components/ui/LoadingSpinner.vue"
import AlertMessage from "@/components/ui/AlertMessage.vue"
import OperationalOrbitalIA from "@/components/ia/OperationalOrbitalIA.vue"
import CarteInfoZone from "@/modules/chef-projet/components/zones/CarteInfoZone.vue"
import { useZoneStore } from "@/stores/zone.js"

const route = useRoute()
const zoneStore = useZoneStore()

const zone = ref(null)
const loading = ref(true)
const error = ref(null)

onMounted(async () => {
    loading.value = true
    error.value = null
    try {
      const data = await zoneStore.fetchZone(route.params.id)
      zone.value = {
        ...data,
        rayon: data.rayon || 2000,
        dateCreation: data.created_at ? data.created_at.split("T")[0] : "",
      }
    } catch (err) {
      error.value = zoneStore.error || "Impossible de charger les détails de cette zone."
    } finally {
      loading.value = false
    }
  })
</script>

