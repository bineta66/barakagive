<template>
  <div class="relative w-full h-full min-h-[420px] select-none flex flex-col">
    <div class="flex items-center justify-between mb-3 flex-shrink-0 gap-3">
      <h3 class="text-sm font-semibold text-slate-500 uppercase tracking-wider">
        Carte interactive du Sénégal
      </h3>
      <div class="flex flex-wrap items-center justify-end gap-3 text-xs text-slate-600">
        <span class="flex items-center gap-1">
          <span class="w-3 h-3 rounded-full bg-red-500 inline-block"></span> Très élevée (80–100)
        </span>
        <span class="flex items-center gap-1">
          <span class="w-3 h-3 rounded-full bg-orange-400 inline-block"></span> Élevée (60–79)
        </span>
        <span class="flex items-center gap-1">
          <span class="w-3 h-3 rounded-full bg-yellow-400 inline-block"></span> Moyenne (40–59)
        </span>
        <span class="flex items-center gap-1">
          <span class="w-3 h-3 rounded-full bg-green-400 inline-block"></span> Faible (0–39)
        </span>
      </div>
    </div>

    <div class="relative flex-1 min-h-[420px] rounded-2xl border border-slate-200 overflow-hidden shadow-sm">
      <LMap
        style="height: 100%; width: 100%"
        :zoom="7"
        :center="[14.4974, -14.4524]"
        :min-zoom="6"
        :max-zoom="11"
        :max-bounds="senegalMaxBounds"
        :max-bounds-viscosity="1"
        :use-global-leaflet="true"
        @ready="onMapReady"
      >
        <LTileLayer
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          attribution="&copy; OpenStreetMap contributors"
        />
      </LMap>

      <div
        v-if="chargement"
        class="absolute inset-0 z-[500] flex items-center justify-center bg-white/60"
      >
        <div class="bg-white rounded-xl shadow-lg px-5 py-4 text-center">
          <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-or mx-auto mb-2"></div>
          <p class="text-sm font-medium text-slate-600">Chargement de la carte...</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { nextTick, watch, onUnmounted } from "vue";
import { LMap, LTileLayer } from "@vue-leaflet/vue-leaflet";
import L from "leaflet";
import "leaflet/dist/leaflet.css";
import geoJsonSenegalRaw from "@/data/senegal-regions.geojson?raw";

const props = defineProps({
  regions: { type: Array, default: () => [] },
  regionSelectionnee: { type: String, default: null },
  chargement: { type: Boolean, default: false },
});

const emit = defineEmits(["region-selectionnee"]);

const geoJsonSenegal = JSON.parse(geoJsonSenegalRaw);
const senegalBounds = L.geoJSON(geoJsonSenegal).getBounds().pad(0.03);
const senegalMaxBounds = [
  [senegalBounds.getSouth(), senegalBounds.getWest()],
  [senegalBounds.getNorth(), senegalBounds.getEast()],
];

const DISPLAY_NAMES = {
  dakar: "Dakar",
  thies: "Thiès",
  diourbel: "Diourbel",
  fatick: "Fatick",
  kaolack: "Kaolack",
  kaffrine: "Kaffrine",
  louga: "Louga",
  "saint louis": "Saint-Louis",
  "saint-louis": "Saint-Louis",
  matam: "Matam",
  tambacounda: "Tambacounda",
  kedougou: "Kédougou",
  kolda: "Kolda",
  sedhiou: "Sédhiou",
  ziguinchor: "Ziguinchor",
};

let mapInstance = null;
let geoJsonLayer = null;
let selectedLayer = null;

function normalizeString(s) {
  if (!s) return "";
  return s
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .replace(/[-_]/g, " ")
    .toLowerCase()
    .trim();
}

function displayName(rawName) {
  const key = normalizeString(rawName);
  return DISPLAY_NAMES[key] || rawName;
}

function getRegionData(nomRegion) {
  const target = normalizeString(nomRegion);
  return props.regions.find((r) => normalizeString(r.region) === target) || null;
}

function getScore(nomRegion) {
  const r = getRegionData(nomRegion);
  if (!r) return null;
  const score = r.score ?? r.score_region;
  return score == null ? null : Number(score);
}

function styleForScore(score, selected = false) {
  let fillColor = "#cbd5e1";
  let color = "#94a3b8";
  if (score >= 80) {
    fillColor = "#ef4444";
    color = "#b91c1c";
  } else if (score >= 60) {
    fillColor = "#fb923c";
    color = "#c2410c";
  } else if (score >= 40) {
    fillColor = "#facc15";
    color = "#a16207";
  } else if (score > 0) {
    fillColor = "#4ade80";
    color = "#15803d";
  }

  return {
    color: selected ? "#021427" : color,
    weight: selected ? 3 : 1.5,
    fillColor,
    fillOpacity: selected ? 0.75 : 0.55,
  };
}

function featureStyle(feature) {
  const name = feature?.properties?.shapeName || feature?.properties?.name || "";
  const selected = normalizeString(name) === normalizeString(props.regionSelectionnee);
  return styleForScore(getScore(name) ?? 0, selected);
}

function tooltipHtml(featureName) {
  const display = displayName(featureName);
  const data = getRegionData(featureName);
  const score = getScore(featureName);
  const total = data?.total_beneficiaires ?? data?.total_beneficiaries ?? 0;
  const niveau = data?.niveau || "";
  const scoreLine =
    score != null
      ? `${score}/100${niveau ? ` — ${niveau}` : ""}`
      : "Aucune donnée";
  const totalLine = total
    ? `<div>${total} bénéficiaire${total > 1 ? "s" : ""}</div>`
    : "";
  return `<strong>${display}</strong><div>${scoreLine}</div>${totalLine}`;
}

function onFeatureClick(event) {
  const layer = event.target;
  const propsData = layer?.feature?.properties;
  if (!propsData) return;
  const raw = propsData.shapeName || propsData.name || "";
  emit("region-selectionnee", displayName(raw));
}

function lockToSenegal({ animate = false } = {}) {
  if (!mapInstance) return;
  mapInstance.setMaxBounds(senegalBounds);
  mapInstance.options.maxBoundsViscosity = 1;
  mapInstance.fitBounds(senegalBounds, { animate, padding: [8, 8] });
}

function addGeoJsonLayer() {
  if (!mapInstance) return;
  if (geoJsonLayer) {
    mapInstance.removeLayer(geoJsonLayer);
  }

  geoJsonLayer = L.geoJSON(geoJsonSenegal, {
    style: featureStyle,
    onEachFeature: (feature, layer) => {
      const name = feature.properties.shapeName || feature.properties.name || "";
      if (name) {
        layer.bindTooltip(() => tooltipHtml(name), {
          sticky: true,
          className: "region-priorite-tooltip",
        });
      }
      layer.on("click", onFeatureClick);
      layer.on("mouseover", () => {
        if (layer !== selectedLayer) {
          layer.setStyle({ weight: 2.5, fillOpacity: 0.8 });
        }
      });
      layer.on("mouseout", () => {
        if (layer !== selectedLayer) {
          geoJsonLayer.resetStyle(layer);
        }
      });
    },
  }).addTo(mapInstance);

  lockToSenegal();
  highlightSelection();
}

function highlightSelection() {
  if (!geoJsonLayer || !mapInstance) return;

  if (selectedLayer) {
    geoJsonLayer.resetStyle(selectedLayer);
    selectedLayer = null;
  }

  if (!props.regionSelectionnee) {
    lockToSenegal();
    return;
  }

  const target = normalizeString(props.regionSelectionnee);
  geoJsonLayer.eachLayer((layer) => {
    const name = layer?.feature?.properties?.shapeName || layer?.feature?.properties?.name || "";
    if (normalizeString(name) === target) {
      selectedLayer = layer;
      layer.setStyle(styleForScore(getScore(name) ?? 0, true));
    } else {
      geoJsonLayer.resetStyle(layer);
    }
  });
}

function restyleAll() {
  if (!geoJsonLayer) return;
  geoJsonLayer.eachLayer((layer) => {
    geoJsonLayer.resetStyle(layer);
  });
  highlightSelection();
}

function onMapReady(map) {
  mapInstance = map;
  addGeoJsonLayer();
  nextTick(() => {
    map.invalidateSize();
    lockToSenegal();
    setTimeout(() => {
      map.invalidateSize();
      lockToSenegal();
    }, 200);
  });
}

watch(
  () => props.regions,
  () => restyleAll(),
  { deep: true }
);

watch(
  () => props.regionSelectionnee,
  () => highlightSelection()
);

onUnmounted(() => {
  if (mapInstance && geoJsonLayer) {
    mapInstance.removeLayer(geoJsonLayer);
  }
});
</script>

<style scoped>
:deep(.leaflet-container) {
  height: 100% !important;
  width: 100% !important;
  min-height: 420px;
  border-radius: 1rem;
  z-index: 1;
}

:deep(.region-priorite-tooltip) {
  background: #0f172a;
  color: #fff;
  border: none;
  border-radius: 0.5rem;
  padding: 0.5rem 0.75rem;
  font-size: 0.8rem;
  box-shadow: 0 1px 2px 0 rgb(0 0 0 / 0.05);
}

:deep(.region-priorite-tooltip::before) {
  border-top-color: #0f172a;
}
</style>
