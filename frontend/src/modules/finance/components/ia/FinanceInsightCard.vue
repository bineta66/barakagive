<template>
  <div class="rounded-xl border p-4 space-y-1 transition-all duration-200"
       :class="cardClass">
    <!-- En-tête -->
    <div class="flex items-center gap-2 mb-2">
      <span class="w-2 h-2 rounded-full flex-shrink-0" :class="dotClass"/>
      <p class="text-[10px] font-bold uppercase tracking-wider" :class="labelClass">
        {{ label }}
      </p>
    </div>
    <!-- Contenu -->
    <p class="text-sm text-slate-700 leading-relaxed whitespace-pre-line">{{ content }}</p>
    <!-- Données chiffrées optionnelles -->
    <div v-if="metric" class="mt-2 pt-2 border-t" :class="borderClass">
      <span class="text-lg font-extrabold" :class="metricClass">{{ metric }}</span>
      <span v-if="metricLabel" class="text-xs text-slate-500 ml-1">{{ metricLabel }}</span>
    </div>
  </div>
</template>

<script setup>
import { computed } from "vue"

const props = defineProps({
  type:        { type: String, default: "info" }, // info | warning | danger | success
  label:       { type: String, required: true },
  content:     { type: String, required: true },
  metric:      { type: String, default: "" },
  metricLabel: { type: String, default: "" },
})

const cardClass = computed(() => ({
  info:    "bg-slate-50 border-slate-200/80",
  warning: "bg-amber-50/60 border-amber-200",
  danger:  "bg-red-50/60 border-red-200",
  success: "bg-emerald-50/60 border-emerald-200",
}[props.type]))

const dotClass = computed(() => ({
  info:    "bg-[#021427]",
  warning: "bg-amber-500",
  danger:  "bg-red-500 animate-pulse",
  success: "bg-emerald-500",
}[props.type]))

const labelClass = computed(() => ({
  info:    "text-[#021427]",
  warning: "text-amber-700",
  danger:  "text-red-700",
  success: "text-emerald-700",
}[props.type]))

const borderClass = computed(() => ({
  info:    "border-slate-200",
  warning: "border-amber-200",
  danger:  "border-red-200",
  success: "border-emerald-200",
}[props.type]))

const metricClass = computed(() => ({
  info:    "text-[#021427]",
  warning: "text-amber-700",
  danger:  "text-red-700",
  success: "text-emerald-700",
}[props.type]))
</script>
