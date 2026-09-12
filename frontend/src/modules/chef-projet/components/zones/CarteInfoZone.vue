<template>
  <div class="bg-white rounded-xl border border-slate-200/60 p-5">
    <div class="flex items-center justify-between mb-4">
      <h3 class="text-lg font-bold text-amber-800">{{ zone.nom }}</h3>
      <span
        class="px-2 py-1 rounded text-xs font-semibold"
        :class="zone.statut === 'Actif' ? 'bg-emerald-100 text-emerald-700' : 'bg-gray-100 text-gray-600'"
      >
        {{ zone.statut }}
      </span>
    </div>

    <div class="grid grid-cols-2 gap-4 text-sm">
      <div>
        <p class="text-xs font-semibold uppercase text-slate-900 mb-1">Région</p>
        <p class="text-gray-700">{{ zone.region }}</p>
      </div>

      <div>
        <p class="text-xs font-semibold uppercase text-slate-900 mb-1">Département</p>
        <p class="text-gray-700">{{ zone.departement }}</p>
      </div>

      <div>
        <p class="text-xs font-semibold uppercase text-slate-900 mb-1">Rayon</p>
        <p class="text-gray-700">{{ zone.rayon }} m</p>
      </div>

      <div>
        <p class="text-xs font-semibold uppercase text-slate-900 mb-1">Latitude</p>
        <p class="text-gray-700">{{ zone.latitude }}</p>
      </div>

      <div>
        <p class="text-xs font-semibold uppercase text-slate-900 mb-1">Longitude</p>
        <p class="text-gray-700">{{ zone.longitude }}</p>
      </div>

      <div>
        <p class="text-xs font-semibold uppercase text-slate-900 mb-1">Date de création</p>
        <p class="text-gray-700">{{ zone.dateCreation }}</p>
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  zone: {
    type: Object,
    default: () => ({}),
  },
})
</script>
