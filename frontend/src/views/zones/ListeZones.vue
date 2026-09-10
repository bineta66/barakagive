<template>
  <div class="p-6 space-y-6 bg-white min-h-screen">
    <div class="flex justify-between items-center">
      <div>
        <h1 class="text-3xl font-bold text-amber-800">Zones d'intervention</h1>
        <p class="text-xs text-gray-500 mt-1">
          Liste des zones géographiques d'intervention humanitaire.
        </p>
      </div>

      <div class="flex gap-3">
        <RouterLink
          to="/zones"
          class="border border-sky-900 text-sky-900 px-4 py-2 rounded-lg text-sm font-semibold flex items-center gap-2"
        >
          <MapPinned :size="18" />
          Carte
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

    <TableauZones :zones="zones" @delete="onDelete" />
  </div>
</template>

<script setup>
import { ref } from "vue"
import { MapPinned, List, Plus } from "lucide-vue-next"
import TableauZones from "@/components/zones/TableauZones.vue"
import { zonesMock } from "@/data/zonesMock.js"

const zones = zonesMock

const onDelete = (id) => {
  zones.value = zones.value.filter((z) => z.id !== id)
}
</script>
