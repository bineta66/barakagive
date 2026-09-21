<template>
  <div class="rounded-2xl bg-white p-5 border border-[#E5E7EB] shadow-sm hover:shadow-md transition-all">
    <!-- Header -->
    <div class="flex items-center justify-between mb-4">
      <div>
        <h3 class="text-base font-bold text-[#021427]">{{ title }}</h3>
        <p v-if="subtitle" class="text-xs text-slate-500 mt-0.5">{{ subtitle }}</p>
      </div>
      <div v-if="$slots.action" class="flex items-center gap-2">
        <slot name="action" />
      </div>
    </div>

    <!-- Empty state -->
    <div v-if="!data || data.length === 0" class="h-64 flex flex-col items-center justify-center text-slate-400 text-sm">
      <svg class="w-10 h-10 mb-2 opacity-50" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
      </svg>
      <span>Aucune donnée disponible pour ce graphique</span>
    </div>

    <!-- Bar Chart -->
    <div v-else-if="type === 'bar'" class="space-y-4 py-2">
      <div
        v-for="(item, index) in data"
        :key="index"
        class="space-y-1.5"
      >
        <div class="flex items-center justify-between text-xs font-medium text-slate-700">
          <span class="truncate max-w-[200px]">{{ item.label }}</span>
          <span class="font-bold text-[#021427]">{{ formatValue(item.value) }}</span>
        </div>
        <div class="w-full bg-slate-100 h-3 rounded-full overflow-hidden flex">
          <div
            class="h-full rounded-full transition-all duration-500 ease-out"
            :style="{
              width: getPercentage(item.value) + '%',
              backgroundColor: item.color || defaultColors[index % defaultColors.length]
            }"
          ></div>
        </div>
      </div>
    </div>

    <!-- Pie / Donut Breakdown Chart -->
    <div v-else-if="type === 'donut' || type === 'pie'" class="grid grid-cols-1 md:grid-cols-2 gap-4 items-center py-2">
      <!-- SVG Donut -->
      <div class="relative flex items-center justify-center">
        <svg class="w-44 h-44 transform -rotate-90" viewBox="0 0 100 100">
          <circle
            cx="50"
            cy="50"
            r="38"
            stroke="#F1F5F9"
            stroke-width="16"
            fill="transparent"
          />
          <circle
            v-for="(segment, idx) in donutSegments"
            :key="idx"
            cx="50"
            cy="50"
            r="38"
            fill="transparent"
            :stroke="segment.color"
            stroke-width="16"
            :stroke-dasharray="`${segment.strokeLength} ${238.76 - segment.strokeLength}`"
            :stroke-dashoffset="-segment.strokeOffset"
            class="transition-all duration-700"
          />
        </svg>
        <div class="absolute inset-0 flex flex-col items-center justify-center text-center">
          <span class="text-xs font-medium text-slate-500">Total</span>
          <span class="text-base font-bold text-[#021427]">{{ formatValue(totalSum) }}</span>
        </div>
      </div>

      <!-- Legend -->
      <div class="space-y-2 text-xs">
        <div
          v-for="(item, idx) in data"
          :key="idx"
          class="flex items-center justify-between p-2 rounded-lg hover:bg-slate-50 transition"
        >
          <div class="flex items-center gap-2 truncate">
            <span
              class="w-3 h-3 rounded-full flex-shrink-0"
              :style="{ backgroundColor: item.color || defaultColors[idx % defaultColors.length] }"
            ></span>
            <span class="text-slate-700 font-medium truncate">{{ item.label }}</span>
          </div>
          <span class="font-bold text-[#021427] ml-2">{{ getPercentage(item.value) }}%</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from "vue"

const props = defineProps({
  title: {
    type: String,
    required: true,
  },
  subtitle: {
    type: String,
    default: "",
  },
  type: {
    type: String,
    default: "bar", // 'bar' | 'donut' | 'pie'
  },
  data: {
    type: Array,
    default: () => [],
  },
  isCurrency: {
    type: Boolean,
    default: true,
  },
})

const defaultColors = [
  "#021427", // Bleu nuit
  "#744D03", // Ocre
  "#10B981", // Emerald
  "#3B82F6", // Blue
  "#F59E0B", // Amber
  "#8B5CF6", // Purple
  "#EC4899", // Pink
]

const totalSum = computed(() => {
  return props.data.reduce((acc, curr) => acc + (Number(curr.value) || 0), 0)
})

const maxValue = computed(() => {
  if (!props.data.length) return 1
  return Math.max(...props.data.map((d) => Number(d.value) || 0), 1)
})

const formatValue = (val) => {
  if (props.isCurrency) {
    return new Intl.NumberFormat("fr-FR", {
      style: "currency",
      currency: "XOF",
      maximumFractionDigits: 0,
    }).format(val || 0).replace("XOF", "FCFA")
  }
  return val
}

const getPercentage = (val) => {
  if (totalSum.value === 0) return 0
  return Math.round(((Number(val) || 0) / totalSum.value) * 100)
}

// Donut calculation (circumference = 2 * PI * 38 ≈ 238.76)
const donutSegments = computed(() => {
  const circum = 238.76
  let accumulatedOffset = 0
  return props.data.map((item, idx) => {
    const val = Number(item.value) || 0
    const pct = totalSum.value > 0 ? val / totalSum.value : 0
    const strokeLength = pct * circum
    const segment = {
      strokeLength,
      strokeOffset: accumulatedOffset,
      color: item.color || defaultColors[idx % defaultColors.length],
    }
    accumulatedOffset += strokeLength
    return segment
  })
})
</script>
