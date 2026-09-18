<template>
  <div class="p-6 space-y-6 bg-white min-h-screen">
    <div class="flex justify-between items-center">
      <div>
        <h1 class="text-3xl font-bold text-or">Zones d'intervention</h1>
        <p class="text-xs text-gray-500 mt-1">
          Liste des zones géographiques d'intervention humanitaire.
        </p>
      </div>

      <div class="flex gap-3">
        <BoutonPrimary to="/chef-projet/zones/creer">
          <Plus :size="18" />
          Nouvelle zone
        </BoutonPrimary>
      </div>
    </div>

    <LoadingSpinner v-if="zoneStore.loading && !zoneStore.zones.length" message="Chargement des zones..." />
    <AlertMessage v-if="feedback.message" :type="feedback.type" :message="feedback.message" class="mb-4" />

    <div class="bg-white rounded-lg border border-slate-200 p-4">
      <div class="flex flex-wrap gap-4 items-center">
        <div class="flex-1 min-w-[200px]">
          <input
            v-model="recherche"
            type="text"
            placeholder="Rechercher une zone..."
            class="w-full h-10 pl-4 pr-4 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-or/30"
          />
        </div>
        <div class="w-64">
          <select v-model="regionFiltre" class="w-full h-10 px-3 border border-gray-300 rounded-md text-sm text-gray-800 focus:outline-none focus:ring-2 focus:ring-or/30 bg-white">
            <option value="">Toutes les régions</option>
            <option v-for="region in regions" :key="region" :value="region">{{ region }}</option>
          </select>
        </div>
        <div class="w-56">
          <select v-model="statutFiltre" class="w-full h-10 px-3 border border-gray-300 rounded-md text-sm text-gray-800 focus:outline-none focus:ring-2 focus:ring-or/30 bg-white">
            <option value="">Tous les statuts</option>
            <option value="true">Actif</option>
            <option value="false">Inactif</option>
          </select>
        </div>
      </div>
    </div>

<TableauZones :zones="zonesFiltrees" @delete="onDelete" />
  </div>

  <OperationalOrbitalIA />
</template>

<script setup>
import { ref, computed, reactive, onMounted } from "vue"
import { Plus } from "lucide-vue-next"
import BoutonPrimary from "@/components/ui/BoutonPrimary.vue"
import LoadingSpinner from "@/components/ui/LoadingSpinner.vue"
import AlertMessage from "@/components/ui/AlertMessage.vue"
import OperationalOrbitalIA from "@/components/ia/OperationalOrbitalIA.vue"
import TableauZones from "@/modules/chef-projet/components/zones/TableauZones.vue"
import { useZoneStore } from "@/stores/zone.js"

const zoneStore = useZoneStore()
const recherche = ref("")
const regionFiltre = ref("")
const statutFiltre = ref("")
const feedback = reactive({ type: "success", message: "" })

onMounted(async () => {
  try {
    await zoneStore.fetchZones()
  } catch (err) {
    feedback.type = "error"
    feedback.message = "Erreur lors du chargement des zones."
  }
})

const regions = computed(() => {
  return [...new Set(zoneStore.zones.map((z) => z.region).filter(Boolean))]
})

const isActive = (statut) => {
  return statut === true || statut === "Actif" || statut === "ACTIF"
}

const zonesFiltrees = computed(() => {
  return zoneStore.zones.filter((zone) => {
    const matchRecherche = !recherche.value || (zone.nom || "").toLowerCase().includes(recherche.value.toLowerCase())
    const matchRegion = !regionFiltre.value || zone.region === regionFiltre.value
    const matchStatut = !statutFiltre.value || isActive(zone.statut) === (statutFiltre.value === "true")
    return matchRecherche && matchRegion && matchStatut
  })
})

const onDelete = async (id) => {
  if (!confirm("Voulez-vous vraiment supprimer cette zone ?")) return
  feedback.message = ""
  try {
    await zoneStore.deleteZone(id)
    feedback.type = "success"
    feedback.message = "Zone supprimée avec succès."
  } catch (err) {
    feedback.type = "error"
    feedback.message = zoneStore.error || "Erreur lors de la suppression de la zone."
  }
}
</script>

