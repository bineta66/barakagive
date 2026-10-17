<template>
  <div class="min-w-0 flex-1 rounded-xl border border-slate-200 bg-white p-3 sm:p-4">
    <div class="mb-3 flex min-w-0 flex-wrap items-start justify-between gap-2">
      <h2 class="min-w-0 text-sm font-semibold leading-6 text-slate-900 sm:text-base">Cartographie opérationnelle // Sénégal</h2>
      <span class="text-xs text-slate-500">COORDS : WGS84 EPSG:4326</span>
    </div>
    <div class="relative aspect-[4/3] min-h-[220px] w-full overflow-hidden rounded-lg bg-neutral-200 sm:aspect-[16/9]">
      <img class="h-full w-full object-cover" src="https://placehold.co/960x540" alt="Aperçu de la carte du Sénégal" />
      <div class="absolute left-2 top-2 max-w-[calc(100%-1rem)] rounded bg-white/90 px-3 py-1 text-xs text-gray-800 sm:left-3 sm:top-3">FLUX EN DIRECT // SENEGAL OPERATIONS</div>
    </div>
    <div class="mt-3 flex flex-wrap items-center justify-between gap-2 text-xs text-gray-600">
      <span class="inline-flex items-center gap-2"><span class="size-3 rounded-sm bg-neutral-300"></span>Zone sans bénéficiaire</span>
      <span>Dernière synchro GPS : 10:42:19 UTC</span>
    </div>
  </div>
</template>

<script setup>
import { computed } from "vue"

const props = defineProps({
  regionSelectionnee: String,
  zoneSelectionnee: String,
  regions: Array,
})

const emit = defineEmits(["update:regionSelectionnee", "update:zoneSelectionnee"])

const selectRegion = (region) => {
  if (props.regionSelectionnee === region) {
    emit("update:regionSelectionnee", "")
    emit("update:zoneSelectionnee", "")
  } else {
    emit("update:regionSelectionnee", region)
    emit("update:zoneSelectionnee", "")
  }
}

const clearRegion = () => {
  emit("update:regionSelectionnee", "")
  emit("update:zoneSelectionnee", "")
}
</script>


