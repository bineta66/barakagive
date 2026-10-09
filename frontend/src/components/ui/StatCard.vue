<template>
  <div
    class="glass-surface p-4 flex justify-between items-center"
  >
    <div>
      <p class="text-sm text-slate-500 mb-1">{{ titre }}</p>
      <p class="text-xl font-bold text-slate-900">{{ valeur }}</p>
    </div>
    <div
      class="w-10 h-10 rounded-lg flex items-center justify-center"
      :class="bgColor"
    >
      <component :is="icone" :size="20" :class="textColor" />
    </div>
  </div>
</template>

<script setup>
import { computed } from "vue";

const props = defineProps({
  titre: { type: String, required: true },
  valeur: { type: [String, Number], required: true },
  icone: { type: [String, Object, Function], required: true },
  couleur: { type: String, default: "sky" },
});

const bgColor = computed(() => {
  const colors = {
    sky: "bg-bleu-accent/10",
    blue: "bg-bleu-nuit/8",
    amber: "bg-bleu-nuit/8",
    emerald: "bg-emerald-50",
    purple: "bg-purple-50",
    red: "bg-red-50",
    orange: "bg-bleu-nuit/8",
    slate: "bg-slate-100",
  };
  return colors[props.couleur] || "bg-slate-50";
});

const textColor = computed(() => {
  const colors = {
    sky: "text-bleu-nuit",
    blue: "text-bleu-nuit",
    amber: "text-bleu-nuit",
    emerald: "text-emerald-600",
    purple: "text-purple-600",
    red: "text-red-600",
    orange: "text-bleu-nuit",
    slate: "text-slate-600",
  };
  return colors[props.couleur] || "text-bleu-nuit";
});
</script>
