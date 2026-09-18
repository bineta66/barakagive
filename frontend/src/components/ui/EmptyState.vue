<template>
  <div class="flex flex-col items-center justify-center p-8 text-center rounded-xl bg-slate-50/70 border border-dashed border-slate-200" :class="containerClass">
    <div class="w-12 h-12 mb-3 rounded-full bg-slate-100 flex items-center justify-center text-slate-400">
      <slot name="icon">
        <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4"></path>
        </svg>
      </slot>
    </div>
    <h3 class="text-base font-semibold text-slate-800 mb-1">{{ titre }}</h3>
    <p v-if="description" class="text-sm text-slate-500 max-w-sm mb-4">{{ description }}</p>
    <slot name="action"></slot>
  </div>
</template>

<script setup>
defineProps({
  titre: {
    type: String,
    default: "Aucune donnée disponible",
  },
  description: {
    type: String,
    default: "Il n'y a actuellement aucun élément à afficher.",
  },
  containerClass: {
    type: String,
    default: "min-h-[220px]",
  },
})
</script>

