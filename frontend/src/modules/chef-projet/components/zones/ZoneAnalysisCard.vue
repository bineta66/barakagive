<template>
  <div class="bg-white border border-slate-200/60 rounded-xl p-4 shadow-sm hover:shadow-md transition-shadow">
    <div class="flex items-start justify-between mb-3">
      <div class="flex items-center gap-2">
        <span class="w-6 h-6 rounded-full bg-bleu-nuit text-white text-xs font-bold flex items-center justify-center">
          {{ rang }}
        </span>
        <div>
          <p class="font-semibold text-bleu-nuit text-sm">{{ zone.nom }}</p>
          <p class="text-[11px] text-gray-500">{{ zone.region }} · {{ zone.departement }}</p>
        </div>
      </div>
      <span
        class="px-2 py-0.5 rounded text-[10px] font-semibold"
        :class="urgencyClass"
      >
        {{ zone.niveau_urgence }}
      </span>
    </div>

    <div class="grid grid-cols-2 gap-3 mb-3">
      <div class="bg-slate-50 p-2 rounded-lg text-center">
        <p class="text-[10px] text-gray-500 uppercase">Score IA</p>
        <p class="font-bold text-or">{{ zone.score_total.toFixed(1) }}</p>
      </div>
      <div class="bg-slate-50 p-2 rounded-lg text-center">
        <p class="text-[10px] text-gray-500 uppercase">Bénéficiaires</p>
        <p class="font-bold text-bleu-nuit">{{ zone.beneficiaires }}</p>
      </div>
    </div>

    <BoutonTertiary @click="$emit('view-detail', zone.id)" class="w-full text-xs">
      Voir plus
    </BoutonTertiary>
  </div>
</template>

<script setup>
import { computed } from "vue"
import BoutonTertiary from "@/components/ui/BoutonTertiary.vue"

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

const emit = defineEmits(["view-detail"])

const urgencyClass = computed(() => {
  switch (props.zone.niveau_urgence) {
    case "Très élevée":
    case "Critique":
      return "bg-red-100 text-red-700"
    case "Élevée":
      return "bg-orange-100 text-orange-700"
    case "Moyenne":
      return "bg-yellow-100 text-yellow-700"
    default:
      return "bg-green-100 text-green-700"
  }
})
</script>