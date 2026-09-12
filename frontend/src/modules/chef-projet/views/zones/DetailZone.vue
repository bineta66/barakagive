<template>
  <div class="p-6 space-y-6 bg-white min-h-screen">
    <div class="flex justify-between items-center border-b border-slate-200 pb-4">
      <div>
        <h1 class="text-3xl font-bold text-amber-800">Détail de la zone</h1>
        <p class="text-sm text-gray-600 mt-1">
          Informations complètes de la zone d'intervention.
        </p>
      </div>

      <div class="flex gap-3">
        <BoutonSecondary to="/chef-projet/zones">
          <List :size="18" />
          Liste des zones
        </BoutonSecondary>
      </div>
    </div>

    <CarteInfoZone :zone="zone" />
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue"
import { useRoute } from "vue-router"
import { MapPinned, List } from "lucide-vue-next"
import BoutonSecondary from "@/components/ui/BoutonSecondary.vue"
import CarteInfoZone from "@/modules/chef-projet/components/zones/CarteInfoZone.vue"
import { zonesMock } from "@/data/zonesMock.js"

const route = useRoute()

const zone = ref({
  nom: "",
  region: "",
  departement: "",
  rayon: 0,
  statut: "Actif",
  latitude: null,
  longitude: null,
  dateCreation: "",
})

onMounted(() => {
  const id = Number(route.params.id)
  const found = zonesMock.value.find((z) => z.id === id)
  if (found) {
    zone.value = found
  }
})
</script>
