<template>
  <div class="flex min-w-0 flex-col items-center gap-5 sm:flex-row sm:gap-6">
    <!-- Donut SVG -->
    <div class="relative flex-shrink-0" :style="{ width: size + 'px', height: size + 'px' }">
      <svg :viewBox="`0 0 ${size} ${size}`" class="w-full h-full -rotate-90">
        <!-- Fond gris -->
        <circle
          :cx="size/2" :cy="size/2" :r="r"
          fill="transparent" stroke="#e2e8f0"
          :stroke-width="thickness"
        />
        <!-- Segments colorés -->
        <circle
          v-for="(seg, i) in segments" :key="i"
          :cx="size/2" :cy="size/2" :r="r"
          fill="transparent"
          :stroke="seg.color"
          :stroke-width="thickness"
          :stroke-dasharray="`${seg.dash} ${circumference}`"
          :stroke-dashoffset="-seg.offset"
          stroke-linecap="butt"
        />
      </svg>
      <!-- Centre : valeur principale -->
      <div class="absolute inset-0 flex flex-col items-center justify-center">
        <span class="font-extrabold text-slate-800" :style="{ fontSize: centerFontSize + 'px' }">
          {{ centerValue }}
        </span>
        <span v-if="centerLabel" class="text-slate-400 mt-0.5" :style="{ fontSize: (centerFontSize * 0.6) + 'px' }">
          {{ centerLabel }}
        </span>
      </div>
    </div>

    <!-- Légende -->
    <div class="w-full min-w-0 flex-1 space-y-2.5 sm:w-auto">
      <div
        v-for="(item, i) in items"
        :key="i"
        class="flex items-center justify-between gap-2"
      >
        <div class="flex items-center gap-2 min-w-0">
          <span class="w-2.5 h-2.5 rounded-full flex-shrink-0" :style="{ backgroundColor: item.color }"/>
          <span class="text-xs text-slate-600 truncate">{{ item.label }}</span>
        </div>
        <div class="text-right flex-shrink-0">
          <span class="text-xs font-bold text-slate-800">{{ item.displayValue }}</span>
          <span v-if="showPercent" class="text-[10px] text-slate-400 ml-1">{{ item.pct }}%</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from "vue"
import { distinctChartColors } from "./chartColors.js"

const props = defineProps({
  /** [{ label, value, color, displayValue? }] */
  items:       { type: Array, required: true },
  size:        { type: Number, default: 120 },
  thickness:   { type: Number, default: 20 },
  centerValue: { type: [String, Number], default: "" },
  centerLabel: { type: String, default: "" },
  centerFontSize: { type: Number, default: 20 },
  showPercent: { type: Boolean, default: true },
})

const r           = computed(() => (props.size / 2) - (props.thickness / 2))
const circumference = computed(() => 2 * Math.PI * r.value)

const total = computed(() => props.items.reduce((s, i) => s + (Number(i.value) || 0), 0))
const segmentColors = computed(() => distinctChartColors(props.items.map(item => item.label)))

const segments = computed(() => {
  if (total.value === 0) return []
  let offset = 0
  return props.items.map((item, index) => {
    const pct  = Number(item.value) / total.value
    const dash = pct * circumference.value
    const seg  = { color: segmentColors.value[index], dash, offset }
    offset += dash
    return seg
  })
})

// Enrichir les items avec pct + displayValue par défaut
const items = computed(() =>
  props.items.map((item, index) => ({
    ...item,
    color: segmentColors.value[index],
    pct: total.value > 0 ? Math.round((Number(item.value) / total.value) * 100) : 0,
    displayValue: item.displayValue ?? Number(item.value).toLocaleString("fr-FR"),
  }))
)
</script>
