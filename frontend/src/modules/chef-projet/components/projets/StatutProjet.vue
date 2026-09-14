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
    default: "PlanifiÃ©",
  },
})

const badgeClass = computed(() => {
  switch (props.status) {
    case "En cours":
      return "bg-or text-white"
    case "PlanifiÃ©":
      return "bg-bleu-nuit text-white"
    case "TerminÃ©":
      return "bg-gray-500 text-white"
    default:
      return "bg-gray-500 text-white"
  }
})
</script>

