<template>
  <div class="h-64 flex items-end gap-8">
    <div
      v-for="plan in data"
      :key="plan.nom"
      class="flex-1 flex flex-col items-center"
    >
      <div
        class="w-full bg-gradient-to-t from-sky-700 to-sky-500 rounded-t-lg h-40 flex items-end justify-center"
        :style="{ height: (plan.valeur / 12) * 160 + 'px' }"
      >
        <span class="text-xs font-bold text-white">{{ plan.valeur }}</span>
      </div>
      <span class="text-sm font-medium text-slate-700 mt-2">{{ plan.nom }}</span>
    </div>
  </div>
</template>

<script setup>
const props = defineProps({
  data: {
    type: Array,
    default: () => [
      { nom: "Starter", valeur: 4 },
      { nom: "Professional", valeur: 8 },
      { nom: "Enterprise", valeur: 3 },
    ],
  },
})
</script>





