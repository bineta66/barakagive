<template>
  <div class="w-full">
    <svg
      class="w-full"
      :viewBox="`0 0 ${W} ${H}`"
      preserveAspectRatio="xMidYMid meet"
    >
      <!-- Grille horizontale -->
      <line
        v-for="i in 5" :key="`g${i}`"
        :x1="ML" :y1="MT + (i-1) * yStep"
        :x2="W - MR" :y2="MT + (i-1) * yStep"
        stroke="#f1f5f9" stroke-width="1"
      />

      <!-- Axe Y labels -->
      <text
        v-for="i in 5" :key="`yl${i}`"
        :x="ML - 6"
        :y="MT + (i-1) * yStep + 4"
        text-anchor="end"
        font-size="9"
        fill="#94a3b8"
      >{{ yLabel(i) }}</text>

      <!-- Séries -->
      <g v-for="(serie, si) in series" :key="si">
        <!-- Aire de remplissage -->
        <path
          v-if="serie.area"
          :d="areaPath(serie)"
          :fill="serie.color"
          fill-opacity="0.08"
        />
        <!-- Ligne -->
        <polyline
          :points="linePoints(serie)"
          fill="none"
          :stroke="serie.color"
          stroke-width="2.5"
          stroke-linecap="round"
          stroke-linejoin="round"
        />
        <!-- Points -->
        <circle
          v-for="(pt, pi) in computedPoints(serie)" :key="pi"
          :cx="pt.x" :cy="pt.y" r="4"
          :fill="serie.color" stroke="white" stroke-width="2"
        />
      </g>

      <!-- Labels X -->
      <text
        v-for="(lbl, i) in xLabels" :key="`xl${i}`"
        :x="xPos(i)" :y="H - 6"
        text-anchor="middle"
        font-size="9"
        fill="#94a3b8"
      >{{ lbl }}</text>
    </svg>

    <!-- Légende -->
    <div class="flex items-center gap-5 mt-3 flex-wrap">
      <div v-for="(s, i) in series" :key="i" class="flex items-center gap-1.5">
        <span class="w-3 h-3 rounded-sm" :style="{ backgroundColor: s.color }"/>
        <span class="text-xs text-slate-500">{{ s.label }}</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from "vue"
import { distinctChartColors } from "./chartColors.js"

const props = defineProps({
  /**
   * series = [{ label, color, area?, data: [number, ...] }]
   * xLabels = [string, ...]
   */
  series:   { type: Array, required: true },
  xLabels:  { type: Array, default: () => [] },
  height:   { type: Number, default: 200 },
  yFormat:  { type: String, default: "number" }, // 'number' | 'fcfa' | 'percent'
})

const series = computed(() => {
  const colors = distinctChartColors(props.series.map(serie => serie.label))
  return props.series.map((serie, index) => ({
  ...serie,
  color: colors[index],
  }))
})

const W = 700, H = props.height
const ML = 48, MR = 8, MT = 12, MB = 24
const chartW = W - ML - MR
const chartH = H - MT - MB
const yStep  = chartH / 4

// Valeur max sur toutes les séries
const maxVal = computed(() => {
  let m = 0
  series.value.forEach(s => s.data.forEach(v => { if (v > m) m = v }))
  return m || 1
})

const yLabel = (i) => {
  const v = (maxVal.value * (4 - (i - 1)) / 4)
  if (props.yFormat === "fcfa") {
    if (v >= 1_000_000) return (v / 1_000_000).toFixed(1) + "M"
    if (v >= 1_000) return (v / 1_000).toFixed(0) + "k"
    return v.toFixed(0)
  }
  if (props.yFormat === "percent") return v.toFixed(0) + "%"
  if (v >= 1_000_000) return (v / 1_000_000).toFixed(1) + "M"
  if (v >= 1_000) return (v / 1_000).toFixed(0) + "k"
  return v.toFixed(0)
}

const n = computed(() => {
  let max = 0
  series.value.forEach(s => { if (s.data.length > max) max = s.data.length })
  return max
})

const xPos = (i) => ML + (n.value <= 1 ? chartW / 2 : (i / (n.value - 1)) * chartW)
const yPos = (v) => MT + chartH - (v / maxVal.value) * chartH

const computedPoints = (serie) =>
  serie.data.map((v, i) => ({ x: xPos(i), y: yPos(v) }))

const linePoints = (serie) =>
  computedPoints(serie).map(p => `${p.x},${p.y}`).join(" ")

const areaPath = (serie) => {
  const pts = computedPoints(serie)
  if (!pts.length) return ""
  const base = MT + chartH
  return `M${pts[0].x},${base} ` +
    pts.map(p => `L${p.x},${p.y}`).join(" ") +
    ` L${pts[pts.length - 1].x},${base} Z`
}
</script>
