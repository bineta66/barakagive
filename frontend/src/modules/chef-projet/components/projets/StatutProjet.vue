<template>
  <span
    class="px-3 py-1 rounded text-xs font-semibold uppercase"
    :class="badgeClass"
  >
    {{ status }}
  </span>
</template>

<script setup>
import { computed } from "vue"

const props = defineProps({
  status: {
    type: String,
    default: "Planifié",
  },
})

const badgeClass = computed(() => {
  switch (props.status) {
    case "En cours":
      return "bg-or text-white"
    case "Planifié":
      return "bg-bleu-nuit text-white"
    case "Terminé":
      return "bg-gray-500 text-white"
    default:
      return "bg-gray-500 text-white"
  }
})
</script>


