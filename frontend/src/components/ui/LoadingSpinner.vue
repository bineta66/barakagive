<template>
  <div class="flex flex-col items-center justify-center p-8 space-y-3" :class="containerClass">
    <div
      class="animate-spin rounded-full border-4 border-solid border-slate-200 border-t-amber-600"
      :class="spinnerSizeClass"
    ></div>
    <p v-if="message" class="text-sm font-medium text-slate-600">{{ message }}</p>
  </div>
</template>

<script setup>
import { computed } from "vue"

const props = defineProps({
  message: {
    type: String,
    default: "Chargement en cours...",
  },
  size: {
    type: String,
    default: "md", // sm, md, lg
  },
  containerClass: {
    type: String,
    default: "min-h-[200px]",
  },
})

const spinnerSizeClass = computed(() => {
  switch (props.size) {
    case "sm":
      return "w-6 h-6 border-2"
    case "lg":
      return "w-12 h-12 border-4"
    case "md":
    default:
      return "w-8 h-8 border-3"
  }
})
</script>
