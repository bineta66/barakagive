<template>
  <div class="w-full h-full relative">
    <LMap
      ref="mapRef"
      :zoom="7"
      :center="[14.4974, -14.4524]"
      :min-zoom="7"
      :use-global-leaflet="true"
      @ready="onMapReady"
      @click="onMapClick"
    >
      <LTileLayer
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        attribution="&copy; OpenStreetMap contributors"
      />

      <!-- Cercles rouges foncés des zones enregistrées -->
      <LCircle
        v-for="zone in zones"
        :key="zone.id"
        :lat-lng="[Number(zone.latitude), Number(zone.longitude)]"
        :radius="zone.rayon"
        :interactive="mode === 'readonly'"
        color="#7F1D1D"
        fill-color="#DC2626"
        :fill-opacity="0.55"
        :weight="4"
      >
        <LTooltip v-if="mode === 'readonly'" permanent class="zone-tooltip">
          <div class="text-center">
            <strong>{{ zone.nom }}</strong><br />
            <span class="text-xs">{{ zone.region }} • {{ zone.rayon }} m</span>
          </div>
        </LTooltip>
        <LPopup v-if="mode === 'readonly'">
          <div class="min-w-[180px]">
            <div class="flex items-center gap-2 mb-2">
              <div class="w-3 h-3 rounded-full bg-red-600"></div>
              <strong class="text-red-900">{{ zone.nom }}</strong>
            </div>
            <div class="space-y-1 text-sm">
              <div class="flex justify-between">
                <span class="text-gray-500">Région</span>
                <span class="font-semibold text-gray-900">{{ zone.region }}</span>
              </div>
              <div class="flex justify-between">
                <span class="text-gray-500">Département</span>
                <span class="font-semibold text-gray-900">{{ zone.departement }}</span>
              </div>
              <div class="flex justify-between">
                <span class="text-gray-500">Rayon</span>
                <span class="font-semibold text-gray-900">{{ zone.rayon }} m</span>
              </div>
              <div class="flex justify-between">
                <span class="text-gray-500">Statut</span>
                <span
                  class="px-2 py-0.5 rounded text-xs font-bold"
                  :class="zone.statut === 'Actif' ? 'bg-bleu-nuit/10 text-bleu-nuit' : 'bg-gray-100 text-gray-600'"
                >
                  {{ zone.statut }}
                </span>
              </div>
              <div class="pt-1 border-t border-gray-100">
                <span class="text-xs text-gray-400">
                  {{ formatCoordinate(zone.latitude) }}, {{ formatCoordinate(zone.longitude) }}
                </span>
              </div>
            </div>
          </div>
        </LPopup>
      </LCircle>

      <!-- Marqueur rouge temporaire -->
      <LMarker
        v-if="tempMarker"
        :lat-lng="tempMarker"
        :icon="redIcon"
      >
        <LPopup>
          <div class="text-center">
            <strong>Nouvelle zone</strong><br />
            <span class="text-xs">{{ form.region || "Région" }}</span>
          </div>
        </LPopup>
      </LMarker>
    </LMap>
  </div>
</template>

<script setup>
import { ref, watch, onUnmounted } from "vue"
import { LMap, LTileLayer, LMarker, LCircle, LTooltip, LPopup } from "@vue-leaflet/vue-leaflet"
import L from "leaflet"
import "leaflet/dist/leaflet.css"

const props = defineProps({
  geojson: {
    type: Object,
    default: null,
  },
  form: {
    type: Object,
    default: () => ({}),
  },
  zones: {
    type: Array,
    default: () => [],
  },
  mode: {
    type: String,
    default: "creation",
  },
})

const emit = defineEmits(["region-selected", "map-click", "submit"])

const formatCoordinate = (value) => {
  const coordinate = Number(value)
  return Number.isFinite(coordinate) ? coordinate.toFixed(4) : "-"
}

const setPointFromLatLng = (latlng) => {
  const latitude = Number(latlng.lat.toFixed(7))
  const longitude = Number(latlng.lng.toFixed(7))

  props.form.latitude = latitude
  props.form.longitude = longitude
  tempMarker.value = [latitude, longitude]

  emit("map-click", { latitude, longitude })
}

const mapRef = ref(null)
const tempMarker = ref(null)
let geoJsonLayer = null
let mapInstance = null
let selectedLayer = null

const redIcon = new L.Icon({
  iconUrl: `data:image/svg+xml;charset=UTF-8,${encodeURIComponent(`<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="#DC2626"><path d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7z"/><circle cx="12" cy="9" r="2.5" fill="white"/></svg>`)}`,
  iconSize: [36, 36],
  iconAnchor: [18, 36],
  popupAnchor: [0, -36],
})

const onFeatureClick = (event) => {
  const layer = event.target
  const props_data = layer?.feature?.properties
  if (!props_data) return

  const region = props_data.shapeName || props_data.name || ""
  const departement = region

  if (props.mode === "creation" && layer === selectedLayer) {
    setPointFromLatLng(event.latlng)
    return
  }

  emit("region-selected", { region, departement })

  if (selectedLayer && geoJsonLayer && selectedLayer !== layer) {
    geoJsonLayer.resetStyle(selectedLayer)
  }
  selectedLayer = layer
  layer.setStyle({
    color: "#EA580C",
    weight: 3,
    fillColor: "#EA580C",
    fillOpacity: 0.25,
  })

  if (mapInstance && layer.getBounds) {
    mapInstance.fitBounds(layer.getBounds(), { padding: [50, 50], maxZoom: 12 })
  }
}

const onMapClick = (event) => {
  if (props.mode !== "creation") return

  setPointFromLatLng(event.latlng)
}

const onMapReady = (map) => {
  mapInstance = map
  addGeoJsonLayer()
}

const addGeoJsonLayer = () => {
  if (!mapInstance || !props.geojson) return

  if (geoJsonLayer) {
    mapInstance.removeLayer(geoJsonLayer)
  }

  geoJsonLayer = L.geoJSON(props.geojson, {
    style: () => ({
      color: "#94A3B8",
      weight: 2,
      fillColor: "#F1F5F9",
      fillOpacity: 0.6,
    }),
    onEachFeature: (feature, layer) => {
      const name = feature.properties.shapeName || feature.properties.name || ""
      if (name) {
        layer.bindTooltip(name, {
          sticky: true,
          className: "region-tooltip",
        })
      }
      layer.on("click", onFeatureClick)
      layer.on("mouseover", () => {
        if (layer !== selectedLayer) {
          layer.setStyle({
            fillColor: "#E2E8F0",
            fillOpacity: 0.8,
          })
        }
      })
      layer.on("mouseout", () => {
        if (layer !== selectedLayer) {
          geoJsonLayer.resetStyle(layer)
        }
      })
    },
  }).addTo(mapInstance)
}

watch(
  () => props.form.submitDone,
  (done) => {
     if (done && props.mode === "creation") {
      tempMarker.value = null
      if (selectedLayer && geoJsonLayer) {
        geoJsonLayer.resetStyle(selectedLayer)
        selectedLayer = null
      }
    }
  }
)

watch(
  () => [props.form.latitude, props.form.longitude],
  ([lat, lng]) => {
    if (lat && lng && props.mode === "creation") {
      tempMarker.value = [lat, lng]
    }
  }
)

onUnmounted(() => {
  if (mapInstance && geoJsonLayer) {
    mapInstance.removeLayer(geoJsonLayer)
  }
})
</script>

<style scoped>
:deep(.leaflet-container) {
  height: 100%;
  width: 100%;
  border-radius: 0.5rem;
}

:deep(.region-tooltip) {
  background: #0f172a;
  color: #fff;
  border: none;
  border-radius: 0.5rem;
  padding: 0.6rem 0.9rem;
  font-weight: 800;
  font-size: 0.95rem;
  box-shadow: 0 1px 2px 0 rgb(0 0 0 / 0.05);
  letter-spacing: 0.02em;
}

:deep(.region-tooltip::before) {
  border-top-color: #0f172a;
}

:deep(.zone-tooltip) {
  background: #7F1D1D;
  color: #fff;
  border: none;
  border-radius: 0.5rem;
  padding: 0.5rem 0.8rem;
  font-weight: 800;
  font-size: 0.9rem;
  box-shadow: 0 1px 2px 0 rgb(0 0 0 / 0.05);
  white-space: nowrap;
  letter-spacing: 0.02em;
}

:deep(.zone-tooltip::before) {
  border-top-color: #7F1D1D;
}

:deep(.leaflet-popup-content) {
  margin: 0;
  padding: 0;
}

:deep(.leaflet-popup-content-wrapper) {
  border-radius: 0.75rem;
  padding: 0;
  box-shadow: 0 1px 2px 0 rgb(0 0 0 / 0.05);
}
</style>
