<template>
  <!-- Barres horizontales avec label + valeur + barre CSS -->
  <div class="space-y-3">
    <div v-if="!items.length" class="text-xs text-slate-400 text-center py-4">
      Aucune donnée disponible
    </div>
    <div
      v-for="(item, i) in displayed"
      :key="i"
      class="flex items-center gap-3"
    >
      <!-- Label -->
      <div class="flex-shrink-0 text-right" :style="{ width: labelWidth + 'px' }">
        <span class="text-xs text-slate-600 font-medium truncate block" :title="item.label">
          {{ truncate(item.label, labelMaxChars) }}
        </span>
      </div>

      <!-- Barre + valeur -->
      <div class="flex-1 flex items-center gap-2">
        <div class="flex-1 bg-slate-100 rounded-full overflow-hidden" :style="{ height: barHeight + 'px' }">
          <div
            class="h-full rounded-full transition-all duration-700"
            :style="{
              width: (max > 0 ? Math.max(2, Math.round((item.value / max) * 100)) : 0) + '%',
              backgroundColor: displayedColors[i],
            }"
          />
        </div>
        <span class="text-xs font-semibold text-slate-700 flex-shrink-0 text-right"
              :style="{ minWidth: valueWidth + 'px' }">
          {{ formatVal(item.value) }}{{ unit ? ' ' + unit : '' }}
        </span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from "vue"
import { distinctChartColors } from "./chartColors.js"

const props = defineProps({
  /** [{ label, value, color? }] */
  items:         { type: Array, required: true },
  maxItems:      { type: Number, default: 8 },
  defaultColor:  { type: String, default: "#021427" },
  barHeight:     { type: Number, default: 8 },
  labelWidth:    { type: Number, default: 110 },
  labelMaxChars: { type: Number, default: 18 },
  valueWidth:    { type: Number, default: 60 },
  unit:          { type: String, default: "" },
  /** 'fcfa' | 'number' | 'percent' */
  format:        { type: String, default: "number" },
})

const displayed = computed(() =>
  [...props.items]
    .sort((a, b) => (Number(b.value) || 0) - (Number(a.value) || 0))
    .slice(0, props.maxItems)
)

const displayedColors = computed(() => distinctChartColors(displayed.value.map(item => item.label)))

const max = computed(() =>
  displayed.value.reduce((m, i) => Math.max(m, Number(i.value) || 0), 1)
)

const truncate = (str, n) =>
  str && str.length > n ? str.slice(0, n - 1) + "…" : str || "—"

const formatVal = (v) => {
  const n = Number(v) || 0
  if (props.format === "fcfa") return n.toLocaleString("fr-FR") + " FCFA"
  if (props.format === "percent") return n.toFixed(1) + "%"
  if (n >= 1_000_000) return (n / 1_000_000).toFixed(1) + "M"
  if (n >= 1_000) return (n / 1_000).toFixed(0) + "k"
  return n.toLocaleString("fr-FR")
}
</script>
