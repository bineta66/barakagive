<template>
  <StatusBadge :statut="status">
    {{ status }}
  </StatusBadge>
</template>

<script setup>
import StatusBadge from "@/components/ui/StatusBadge.vue"

const props = defineProps({
  status: {
    type: String,
    default: "Planifié",
  },
})
</script>


