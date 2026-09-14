<template>
  <div class="p-6 space-y-6 bg-white min-h-screen">
    <div class="flex justify-between items-center">
      <div>
        <h1 class="text-3xl font-bold text-or">Zones d'intervention</h1>
        <p class="text-xs text-gray-500 mt-1">
          Liste des zones gÃ©ographiques d'intervention humanitaire.
        </p>
      </div>

      <div class="flex gap-3">
        <BoutonPrimary to="/chef-projet/zones/creer">
          <Plus :size="18" />
          Nouvelle zone
        </BoutonPrimary>
      </div>
    </div>

    <div class="bg-white rounded-lg border border-slate-200 p-4">
      <div class="flex flex-wrap gap-4 items-center">
        <div class="flex-1 min-w-[200px]">
          <input
            v-model="recherche"
            type="text"
            placeholder="Rechercher une zone..."
            class="w-full h-10 pl-4 pr-4 border border-gray-400 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-or/30"
          />
        </div>
        <div class="w-64">
          <select v-model="regionFiltre" class="w-full h-10 px-3 border border-gray-400 rounded-md text-sm text-gray-800 focus:outline-none focus:ring-2 focus:ring-or/30">
            <option value="">Toutes les rÃ©gions</option>
            <option v-for="region in regions" :key="region" :value="region">{{ region }}</option>
          </select>
        </div>
        <div class="w-56">
          <select v-model="statutFiltre" class="w-full h-10 px-3 border border-gray-400 rounded-md text-sm text-gray-800 focus:outline-none focus:ring-2 focus:ring-or/30">
            <option value="">Tous les statuts</option>
            <option value="Actif">Actif</option>
            <option value="Inactif">Inactif</option>
          </select>
        </div>
      </div>
    </div>

    <TableauZones :zones="zonesFiltrees" @delete="onDelete" />
  </div>
</template>

<script setup>
import { ref, computed } from "vue"
import { Plus } from "lucide-vue-next"
import BoutonPrimary from "@/components/ui/BoutonPrimary.vue"
import TableauZones from "@/modules/chef-projet/components/zones/TableauZones.vue"
import { zonesMock } from "@/data/zonesMock.js"

const zones = zonesMock
const recherche = ref("")
const regionFiltre = ref("")
const statutFiltre = ref("")

const regions = [...new Set(zones.value.map((z) => z.region))]

const zonesFiltrees = computed(() => {
  return zones.value.filter((zone) => {
    const matchRecherche = !recherche.value || zone.nom.toLowerCase().includes(recherche.value.toLowerCase())
    const matchRegion = !regionFiltre.value || zone.region === regionFiltre.value
    const matchStatut = !statutFiltre.value || zone.statut === statutFiltre.value
    return matchRecherche && matchRegion && matchStatut
  })
})

const onDelete = (id) => {
  zones.value = zones.value.filter((z) => z.id !== id)
}
</script>

