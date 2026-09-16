<template>
  <div
    class="bg-white border border-slate-200/60 rounded-xl p-4 flex justify-between items-center"
  >
    <div>
      <p class="text-sm text-slate-500 mb-1">{{ titre }}</p>
      <p class="text-2xl font-bold text-slate-900">{{ valeur }}</p>
    </div>
    <div
      class="w-12 h-12 rounded-xl flex items-center justify-center"
      :class="bgColor"
    >
      <component :is="icone" :size="24" :class="textColor" />
    </div>
  </div>
</template>

<script setup>
import { computed } from "vue"

const props = defineProps({
  titre: { type: String, required: true },
  valeur: { type: [String, Number], required: true },
  icone: { type: [String, Object, Function], required: true },
  couleur: { type: String, default: "sky" },
})

const bgColor = computed(() => {
  const colors = {
    sky: "bg-sky-50",
    amber: "bg-or/10",
    emerald: "bg-emerald-50",
    purple: "bg-purple-50",
    red: "bg-red-50",
    orange: "bg-or/10",
    blue: "bg-sky-50",
    slate: "bg-slate-100",
  }
  return colors[props.couleur] || "bg-slate-50"
})

const textColor = computed(() => {
  const colors = {
    sky: "text-sky-600",
    amber: "text-or",
    emerald: "text-emerald-600",
    purple: "text-purple-600",
    red: "text-red-600",
    orange: "text-or",
    blue: "text-sky-600",
    slate: "text-slate-600",
  }
  return colors[props.couleur] || "text-slate-600"
})
</script>



