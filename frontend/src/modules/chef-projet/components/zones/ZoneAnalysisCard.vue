<template>
  <div class="bg-white border border-slate-200/60 rounded-xl p-4 shadow-sm hover:shadow-md transition-shadow">
    <div class="flex items-start justify-between mb-3">
      <div class="flex items-center gap-2">
        <span class="w-6 h-6 rounded-full bg-bleu-nuit text-white text-xs font-bold flex items-center justify-center">
          {{ rang }}
        </span>
        <div>
          <p class="font-semibold text-bleu-nuit text-sm">{{ zone.name }}</p>
          <p class="text-[11px] text-gray-500">{{ zone.region }} · {{ zone.departement }}</p>
        </div>
      </div>
      <span
        class="px-2 py-0.5 rounded text-[10px] font-semibold"
        :class="levelClass"
      >
        {{ levelLabel }}
      </span>
    </div>

    <div class="grid grid-cols-2 gap-3 mb-3">
      <div class="bg-slate-50 p-2 rounded-lg text-center">
        <p class="text-[10px] text-gray-500 uppercase">Score IA</p>
        <p class="font-bold text-or">{{ zone.score.toFixed(1) }}</p>
      </div>
      <div class="bg-slate-50 p-2 rounded-lg text-center">
        <p class="text-[10px] text-gray-500 uppercase">Bénéficiaires</p>
        <p class="font-bold text-bleu-nuit">{{ zone.beneficiaries }}</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from "vue"

const props = defineProps({
  zone: {
    type: Object,
    required: true,
  },
  rang: {
    type: Number,
    required: true,
  },
})

const levelClass = computed(() => {
  switch (props.zone.level) {
    case "TRES_ELEVEE":
      return "bg-red-100 text-red-700"
    case "ELEVEE":
      return "bg-orange-100 text-orange-700"
    case "MOYENNE":
      return "bg-yellow-100 text-yellow-700"
    case "FAIBLE":
      return "bg-green-100 text-green-700"
    case "AUCUNE_DONNEE":
      return "bg-gray-100 text-gray-700"
    default:
      return "bg-green-100 text-green-700"
  }
})

const levelLabel = computed(() => {
  switch (props.zone.level) {
    case "TRES_ELEVEE":
      return "Très élevée"
    case "ELEVEE":
      return "Élevée"
    case "MOYENNE":
      return "Moyenne"
    case "FAIBLE":
      return "Faible"
    case "AUCUNE_DONNEE":
      return "Aucune donnée"
    default:
      return props.zone.level
  }
})
</script>