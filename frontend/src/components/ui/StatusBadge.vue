<template>
  <span
    class="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-medium font-poppins whitespace-nowrap"
    :class="badgeClass"
  >
    <slot />
  </span>
</template>

<script setup>
import { computed } from "vue"

const props = defineProps({
  statut: {
    type: String,
    required: true,
  },
})

const badgeClass = computed(() => {
  const s = props.statut
  switch (s) {
    case "Actif":
    case "ACTIF":
    case "ReÃ§u":
      return "bg-emerald-600 text-white"
    case "En cours":
    case "EN COURS":
    case "BudgÃ©tÃ©":
    case "BudgÃ©tisÃ©":
      return "bg-or text-white"
    case "PlanifiÃ©":
    case "PLANIFIÃ‰":
    case "PlanifiÃ©e":
    case "Ã€ budgÃ©tiser":
    case "Ã€ budgÃ©tisÃ©":
      return "bg-bleu-nuit text-white"
    case "TerminÃ©":
    case "TERMINÃ‰":
    case "TerminÃ©e":
      return "bg-gray-500 text-white"
    case "Inactif":
    case "INACTIF":
    case "ModÃ©rÃ©":
    case "En attente":
    case "Ã€ budgÃ©tiser":
      return "bg-gray-300 text-white"
    case "Critique":
    case "CRITIQUE":
      return "bg-red-600 text-white"
    case "Ã‰levÃ©":
      return "bg-or text-white"
    default:
      return "bg-gray-300 text-white"
  }
})
</script>

