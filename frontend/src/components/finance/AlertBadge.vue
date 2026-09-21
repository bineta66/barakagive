<template>
  <span
    class="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-medium border transition-all"
    :class="badgeStyle"
  >
    <span class="w-1.5 h-1.5 rounded-full" :class="dotStyle"></span>
    {{ formattedText }}
  </span>
</template>

<script setup>
import { computed } from "vue"

const props = defineProps({
  status: {
    type: String,
    required: true,
    default: "EN_ATTENTE",
  },
  label: {
    type: String,
    default: "",
  },
})

const normalizedStatus = computed(() => {
  return String(props.status || "").toUpperCase()
})

const badgeStyle = computed(() => {
  const s = normalizedStatus.value
  if (["APPROUVE", "APPROUVÉE", "VERIFIE", "VÉRIFIÉ", "CONFORME"].includes(s)) {
    return "bg-emerald-50 text-emerald-700 border-emerald-200"
  }
  if (["EN_ATTENTE", "A_VERIFIER", "À VÉRIFIER", "BROUILLON", "EN_COURS"].includes(s)) {
    return "bg-amber-50 text-amber-700 border-amber-200"
  }
  if (["REJETE", "REJETÉE", "NON_CONFORME", "NON CONFORME"].includes(s)) {
    return "bg-rose-50 text-rose-700 border-rose-200"
  }
  if (["CLOTURE", "CLÔTURÉ"].includes(s)) {
    return "bg-slate-100 text-slate-700 border-slate-300"
  }
  return "bg-gray-100 text-gray-700 border-gray-200"
})

const dotStyle = computed(() => {
  const s = normalizedStatus.value
  if (["APPROUVE", "APPROUVÉE", "VERIFIE", "VÉRIFIÉ", "CONFORME"].includes(s)) {
    return "bg-emerald-500 animate-pulse"
  }
  if (["EN_ATTENTE", "A_VERIFIER", "À VÉRIFIER", "BROUILLON", "EN_COURS"].includes(s)) {
    return "bg-amber-500"
  }
  if (["REJETE", "REJETÉE", "NON_CONFORME", "NON CONFORME"].includes(s)) {
    return "bg-rose-500"
  }
  if (["CLOTURE", "CLÔTURÉ"].includes(s)) {
    return "bg-slate-500"
  }
  return "bg-gray-500"
})

const formattedText = computed(() => {
  if (props.label) return props.label

  const s = normalizedStatus.value
  const map = {
    APPROUVE: "Approuvée",
    APPROUVÉE: "Approuvée",
    VERIFIE: "Vérifiée",
    CONFORME: "Conforme",
    EN_ATTENTE: "En attente",
    A_VERIFIER: "À vérifier",
    BROUILLON: "Brouillon",
    EN_COURS: "En cours",
    REJETE: "Rejetée",
    REJETÉE: "Rejetée",
    NON_CONFORME: "Non conforme",
    CLOTURE: "Clôturé",
  }
  return map[s] || props.status
})
</script>
