<template>
  <div class="relative min-w-0 w-full" :style="{ height: `${height}px` }">
    <canvas ref="canvas" class="max-w-full" />
    <div v-if="type === 'doughnut' && centerValue !== undefined" class="pointer-events-none absolute inset-0 flex flex-col items-center justify-center">
      <span class="text-xl font-bold text-slate-800">{{ centerValue }}%</span>
      <span class="text-[10px] text-slate-500">{{ centerLabel }}</span>
    </div>
  </div>
</template>

<script setup>
import { onBeforeUnmount, onMounted, ref, watch } from 'vue'
import {
  ArcElement, BarController, BarElement, CategoryScale, Chart, DoughnutController,
  Filler, Legend, LinearScale, LineController, LineElement, PointElement, Tooltip,
} from 'chart.js'
import { CHART_COLORS, chartColor, distinctChartColors } from './chartColors.js'

Chart.register(
  ArcElement, BarController, BarElement, CategoryScale, DoughnutController,
  Filler, Legend, LinearScale, LineController, LineElement, PointElement, Tooltip,
)

const props = defineProps({
  type: { type: String, required: true },
  data: { type: Object, required: true },
  height: { type: Number, default: 260 },
  horizontal: { type: Boolean, default: false },
  valueFormat: { type: String, default: 'number' },
  centerValue: { type: Number, default: undefined },
  centerLabel: { type: String, default: '' },
  axisColor: { type: String, default: '#64748b' },
  legendColor: { type: String, default: '#475569' },
  gridColor: { type: String, default: '' },
  seriesColor: { type: String, default: '' },
})

const canvas = ref(null)
let chart
const copyData = data => {
  const result = structuredClone(data)
  const categorical = ['doughnut', 'pie'].includes(props.type)
  const statusBars = props.type === 'bar' && (result.labels || []).some(label => /planifi|en cours|termine|archive|annul|attente|actif|rejet|suspend/i.test(String(label)))
  const categoryBars = props.type === 'bar' && result.datasets?.length === 1 && !props.seriesColor
  const seriesColors = distinctChartColors((result.datasets || []).map(dataset => dataset.label || ''))
  const categoryColors = distinctChartColors(result.labels || [])
  const categoryPalette = Object.values(CHART_COLORS)
  result.datasets = (result.datasets || []).map((dataset, index) => {
    const color = result.datasets.length > 1 ? seriesColors[index] : chartColor(dataset.label, index)
    if (categorical) {
      dataset.backgroundColor = (dataset.data || []).map((_, itemIndex) => {
        if (!props.seriesColor) return categoryColors[itemIndex]
        return itemIndex === 0 ? props.seriesColor : `${props.seriesColor}35`
      })
      dataset.borderColor = '#ffffff'
    } else {
      const seriesColor = props.seriesColor || color
      const [red, green, blue] = seriesColor.slice(1).match(/.{2}/g).map(value => Number.parseInt(value, 16))
      dataset.backgroundColor = categoryBars && !statusBars
        ? (dataset.data || []).map((_, itemIndex) => categoryPalette[itemIndex % categoryPalette.length])
        : statusBars && !props.seriesColor
        ? (dataset.data || []).map((_, itemIndex) => categoryColors[itemIndex])
        : props.type === 'line' && dataset.fill
          ? `rgba(${red}, ${green}, ${blue}, 0.12)`
          : seriesColor
      dataset.borderColor = seriesColor
    }
    return dataset
  })
  return result
}
const formatter = value => props.valueFormat === 'currency'
  ? `${new Intl.NumberFormat('fr-FR', { maximumFractionDigits: 0 }).format(value)} FCFA`
  : props.valueFormat === 'percent' ? `${value}%` : new Intl.NumberFormat('fr-FR').format(value)
const axisFormatter = value => props.valueFormat === 'currency'
  ? `${new Intl.NumberFormat('fr-FR', { notation: 'compact', maximumFractionDigits: 1 }).format(value)} FCFA`
  : formatter(value)

const createOptions = () => {
  const doughnut = props.type === 'doughnut'
  const options = {
    responsive: true,
    maintainAspectRatio: false,
    animation: { duration: 250 },
    interaction: { mode: props.type === 'line' ? 'index' : 'nearest', intersect: props.type !== 'line' },
    plugins: {
      legend: { display: !doughnut && !(props.type === 'bar' && props.data.datasets?.length === 1), position: 'bottom', labels: { usePointStyle: true, boxWidth: 8, boxHeight: 8, padding: 20, color: props.legendColor, font: { size: 12 } } },
      tooltip: { callbacks: { label: context => `${context.dataset.label ? `${context.dataset.label}: ` : ''}${formatter(context.parsed.y ?? context.parsed.x ?? context.parsed)}` } },
    },
  }
  if (!doughnut) {
    options.scales = {
      x: { beginAtZero: true, grid: { display: props.type !== 'line', color: props.gridColor || '#f1f5f9' }, ticks: { color: props.axisColor, maxRotation: 0, autoSkip: true } },
      y: { beginAtZero: true, grid: { display: props.type === 'line', color: props.gridColor || '#e2e8f0' }, ticks: { color: props.axisColor } },
    }
    if (props.horizontal) options.indexAxis = 'y'
    const valueAxis = props.horizontal ? 'x' : 'y'
    options.scales[valueAxis].ticks.precision = 0
    if (props.valueFormat !== 'number') options.scales[valueAxis].ticks.callback = value => axisFormatter(value)
    if (props.type === 'line') {
      options.scales.x.grid.display = false
      options.scales.x.ticks.maxRotation = 0
      options.scales.y.grace = '8%'
      options.elements = { line: { tension: 0.25, borderWidth: 2.5, capBezierPoints: true }, point: { radius: 3, hoverRadius: 6, hitRadius: 12, borderWidth: 2 } }
    }
  }
  return options
}

const createChart = () => {
  if (!canvas.value) return
  const existingChart = Chart.getChart(canvas.value)
  if (existingChart) existingChart.destroy()
  if (canvas.value) delete canvas.value.__barakaChart
  chart = null
  chart = new Chart(canvas.value, { type: props.type, data: copyData(props.data), options: createOptions() })
  canvas.value.__barakaChart = chart
}

const updateChart = () => {
  if (!chart) return
  if (chart.config.type !== props.type) {
    createChart()
    return
  }
  chart.data = copyData(props.data)
  chart.options = createOptions()
  chart.update('none')
}

onMounted(createChart)
watch(() => props.data, updateChart)
watch(() => [props.type, props.horizontal, props.valueFormat, props.axisColor, props.legendColor, props.gridColor, props.seriesColor], updateChart)
onBeforeUnmount(() => {
  const existingChart = canvas.value && Chart.getChart(canvas.value)
  if (existingChart) existingChart.destroy()
  if (canvas.value) delete canvas.value.__barakaChart
  chart = null
})
</script>
