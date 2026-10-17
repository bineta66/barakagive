<template>
  <div class="space-y-3">
    <div class="flex flex-wrap items-center gap-3 text-xs text-slate-600">
      <span v-for="item in legend" :key="item.label" class="inline-flex items-center gap-1.5">
        <span class="size-2.5 rounded-full" :style="{ backgroundColor: item.color }"></span>{{ item.label }}
      </span>
      <button v-if="selectedRegion" type="button" class="ml-auto font-semibold text-bleu-nuit underline" @click="clearRegion">Voir toutes les regions</button>
      <span v-if="selectedRegion" class="w-full text-slate-500">Region selectionnee : {{ selectedRegion }}</span>
    </div>
    <div class="relative h-[420px] overflow-hidden rounded-xl border border-slate-200">
      <LMap :zoom="7" :center="[14.4974, -14.4524]" :min-zoom="6" :max-zoom="13" :use-global-leaflet="true" @ready="onMapReady">
        <LTileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" attribution="&copy; OpenStreetMap contributors" />
        <LGeoJson v-if="regionsGeoJson" :geojson="regionsGeoJson" :options="regionOptions" />

        <template v-for="zone in validZones" :key="`zone-${zone.id}`">
          <LCircle :lat-lng="[zone.lat, zone.lng]" :radius="zone.rayon" :color="priorityColor(zone.score_moyen)" :fill-color="priorityColor(zone.score_moyen)" :fill-opacity="0.22" :weight="2">
            <LTooltip sticky>
              <div class="space-y-1 text-xs">
                <p class="font-bold">{{ zone.nom }} - {{ zone.region }}</p>
                <p>Niveau de priorite : {{ priorityLabel(zone.score_moyen) }}</p>
                <p>Beneficiaires de la zone : {{ zone.total_beneficiaires }}</p>
                <p>Beneficiaires prioritaires : {{ zone.beneficiaires_prioritaires }}</p>
              </div>
            </LTooltip>
          </LCircle>
          <LCircleMarker :lat-lng="[zone.lat, zone.lng]" :radius="zoneMarkerRadius" :color="priorityColor(zone.score_moyen)" :fill-color="priorityColor(zone.score_moyen)" :fill-opacity="0.95" :weight="2">
            <LTooltip sticky>
              <div class="space-y-1 text-xs">
                <p class="font-bold">{{ zone.nom }} - {{ zone.region }}</p>
                <p>Niveau de priorite : {{ priorityLabel(zone.score_moyen) }}</p>
                <p>Total beneficiaires : {{ zone.total_beneficiaires }}</p>
                <p>Dont prioritaires : {{ zone.beneficiaires_prioritaires }}</p>
              </div>
            </LTooltip>
          </LCircleMarker>
        </template>

        <LMarker v-for="cluster in clusters" :key="cluster.id" :lat-lng="[cluster.lat, cluster.lng]" :icon="iconFor(cluster.score)">
          <LPopup>
            <div v-if="cluster.points.length > 1" class="min-w-44 space-y-2 text-sm">
              <p class="font-semibold">{{ cluster.points.length }} beneficiaire(s) a proximite</p>
              <button class="text-xs font-medium text-bleu-nuit underline" @click="zoomToCluster(cluster)">Zoomer pour detailler</button>
              <ul class="max-h-40 space-y-1 overflow-auto"><li v-for="point in cluster.points" :key="point.id">{{ point.nom }} - {{ point.score == null ? 'Non evalue' : `${point.score}/100` }}</li></ul>
            </div>
            <div v-else class="min-w-44 space-y-1 text-sm">
              <p class="font-semibold">{{ cluster.points[0].nom }}</p>
              <p>Zone : {{ cluster.points[0].zone || 'Non renseignee' }}</p>
              <p>Region : {{ cluster.points[0].region || 'Non renseignee' }}</p>
              <p>Score de vulnerabilite : {{ cluster.points[0].score == null ? 'Non evalue' : `${cluster.points[0].score}/100` }}</p>
              <p>Priorite : {{ cluster.points[0].priorite || 'Non evaluee' }}</p>
              <p>Besoin principal : {{ cluster.points[0].besoin_principal || 'Non renseigne' }}</p>
              <p>Statut : {{ cluster.points[0].statut }}</p>
              <p>Campagne : {{ cluster.points[0].campagne }}</p>
            </div>
          </LPopup>
        </LMarker>
      </LMap>
      <div v-if="validZones.length === 0" class="absolute bottom-2 left-2 rounded bg-white/90 px-3 py-2 text-xs text-slate-500">Aucune zone avec coordonnées dans cette région et ces filtres.</div>
    </div>
  </div>
</template>

<script setup>
import { computed, onUnmounted, ref } from 'vue'
import { LMap, LTileLayer, LMarker, LPopup, LTooltip, LGeoJson, LCircle, LCircleMarker } from '@vue-leaflet/vue-leaflet'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'
import geoJsonRaw from '@/data/senegal-regions.geojson?raw'

const props = defineProps({ points: { type: Array, default: () => [] }, zones: { type: Array, default: () => [] } })
const zoom = ref(7)
const selectedRegion = ref('')
let leafletMap = null

const onMapReady = map => {
  leafletMap = map
  zoom.value = map.getZoom()
  map.on('zoomend', () => { zoom.value = map.getZoom() })
}
onUnmounted(() => { leafletMap?.off('zoomend') })

const regionsGeoJson = computed(() => {
  try { return JSON.parse(geoJsonRaw) } catch { return null }
})
const normalizedRegion = value => String(value || '').normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLocaleLowerCase().trim()
const regionOptions = computed(() => ({
  style: feature => {
    const name = feature?.properties?.shapeName || feature?.properties?.name
    const selected = selectedRegion.value && normalizedRegion(name) === normalizedRegion(selectedRegion.value)
    return { color: selected ? '#021427' : '#94a3b8', weight: selected ? 2 : 1, fillColor: selected ? '#bfdbfe' : '#f8fafc', fillOpacity: selected ? 0.28 : 0.08 }
  },
  onEachFeature: (feature, layer) => {
    const name = feature?.properties?.shapeName || feature?.properties?.name
    if (name) {
      layer.bindTooltip(name, { sticky: true })
      layer.on('click', () => {
        selectedRegion.value = name
        leafletMap?.fitBounds(layer.getBounds(), { padding: [24, 24], maxZoom: 10 })
      })
    }
  },
}))

const legend = [
  { label: 'Faible', color: '#16a34a' },
  { label: 'Moyenne', color: '#eab308' },
  { label: 'Elevee', color: '#f97316' },
  { label: 'Critique', color: '#dc2626' },
  { label: 'Aucune donnee', color: '#64748b' },
]
const priorityColor = score => score == null ? '#64748b' : Number(score) >= 80 ? '#dc2626' : Number(score) >= 60 ? '#f97316' : Number(score) >= 40 ? '#eab308' : '#16a34a'
const priorityLabel = score => score == null ? 'Non evaluee' : Number(score) >= 80 ? 'Critique' : Number(score) >= 60 ? 'Elevee' : Number(score) >= 40 ? 'Moyenne' : 'Faible'
const zoneMarkerRadius = computed(() => zoom.value >= 10 ? 11 : zoom.value >= 8 ? 9 : 7)
const validPoints = computed(() => props.points.filter(point => {
  const inRegion = !selectedRegion.value || normalizedRegion(point.region) === normalizedRegion(selectedRegion.value)
  return inRegion && Number.isFinite(Number(point.lat)) && Number.isFinite(Number(point.lng))
}))
const validZones = computed(() => props.zones.filter(zone => {
  const inRegion = !selectedRegion.value || normalizedRegion(zone.region) === normalizedRegion(selectedRegion.value)
  return inRegion && Number.isFinite(Number(zone.lat)) && Number.isFinite(Number(zone.lng)) && Number(zone.rayon) > 0
}))

const clusters = computed(() => {
  const grid = zoom.value >= 13 ? 0 : 40 * 360 / (256 * (2 ** zoom.value))
  if (!grid) return validPoints.value.map(point => ({ id: point.id, lat: Number(point.lat), lng: Number(point.lng), score: point.score, points: [point] }))
  const grouped = new Map()
  for (const point of validPoints.value) {
    const lat = Number(point.lat), lng = Number(point.lng)
    const key = `${Math.floor(lat / grid)}:${Math.floor(lng / grid)}`
    if (!grouped.has(key)) grouped.set(key, [])
    grouped.get(key).push(point)
  }
  return [...grouped.entries()].map(([id, points]) => ({
    id, points, lat: Number(points[0].lat), lng: Number(points[0].lng),
    score: Math.max(...points.map(point => point.score == null ? -1 : Number(point.score))),
  }))
})

const iconFor = score => {
  const color = score == null || Number(score) < 0 ? '#64748b' : priorityColor(score)
  return L.divIcon({
    className: 'dashboard-priority-marker',
    html: `<span style="display:block;width:12px;height:12px;border:2px solid white;border-radius:50%;background:${color};box-shadow:0 1px 5px #33415599"></span>`,
    iconSize: [12, 12], iconAnchor: [6, 6],
  })
}
const zoomToCluster = cluster => leafletMap?.setView([cluster.lat, cluster.lng], Math.min(13, leafletMap.getZoom() + 2))
const clearRegion = () => {
  selectedRegion.value = ''
  leafletMap?.setView([14.4974, -14.4524], 7)
}
</script>
