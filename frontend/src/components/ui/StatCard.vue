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

// Respecte strictement le design system BarakaGive : bleu-nuit, bleu-accent, rose-baraka
const bgColor = computed(() => {
  const c = props.couleur?.toLowerCase() || "";
  if (c.includes("rose") || c.includes("red") || c.includes("danger") || c.includes("alert")) {
    return "bg-rose-baraka/10";
  }
  if (c.includes("accent") || c.includes("sky") || c.includes("blue") || c.includes("second")) {
    return "bg-bleu-accent/10";
  }
  return "bg-bleu-nuit/10";
});

const textColor = computed(() => {
  const c = props.couleur?.toLowerCase() || "";
  if (c.includes("rose") || c.includes("red") || c.includes("danger") || c.includes("alert")) {
    return "text-rose-baraka";
  }
  if (c.includes("accent") || c.includes("sky") || c.includes("blue") || c.includes("second")) {
    return "text-bleu-accent";
  }
  return "text-bleu-nuit";
});
</script>
