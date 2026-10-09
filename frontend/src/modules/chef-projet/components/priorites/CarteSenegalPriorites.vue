<template>
  <div class="relative w-full h-full min-h-[420px] select-none flex flex-col">
    <div class="flex items-center justify-between mb-3 flex-shrink-0 gap-3">
      <h3 class="text-sm font-semibold text-slate-500 uppercase tracking-wider">
        Carte interactive du Sénégal
      </h3>
      <div class="flex flex-wrap items-center gap-x-3 gap-y-1 text-[11px] text-slate-600" aria-label="Légende des niveaux de priorité">
        <span class="inline-flex items-center gap-1"><i class="h-2.5 w-2.5 rounded-full bg-red-600"></i>Très élevée</span>
        <span class="inline-flex items-center gap-1"><i class="h-2.5 w-2.5 rounded-full bg-orange-500"></i>Élevée</span>
        <span class="inline-flex items-center gap-1"><i class="h-2.5 w-2.5 rounded-full bg-yellow-500"></i>Moyenne</span>
        <span class="inline-flex items-center gap-1"><i class="h-2.5 w-2.5 rounded-full bg-green-600"></i>Faible</span>
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
          <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-bleu-nuit mx-auto mb-2"></div>
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
  zones: { type: Array, default: () => [] },
  regionSelectionnee: { type: String, default: null },
  zoneSelectionneeId: { type: String, default: null },
  chargement: { type: Boolean, default: false },
});

const emit = defineEmits(["region-selectionnee", "zone-selectionnee"]);

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
let zoneMarkersLayer = null;
const zoneMarkers = new Map();

const unavailable = "Information non disponible dans les données fournies.";

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
  if (r.couleur === "grey" || r.niveau === "Aucune donnée") return null;
  const score = r.score ?? r.score_region;
  return score == null ? null : Number(score);
}

function styleForScore(_score, selected = false) {
  const score = _score == null ? null : Number(_score);
  const data = Number.isFinite(score) ? score : null;
  const fillColor = data == null ? "#cbd5e1" : data >= 80 ? "#d20c4f" : data >= 60 ? "#f97316" : data >= 40 ? "#eab308" : "#16a34a";
  return {
    color: selected ? "#00313c" : "#64748b",
    weight: selected ? 3 : 2,
    fillColor,
    fillOpacity: data == null ? 0.55 : selected ? 0.82 : 0.68,
  };
}

function featureStyle(feature) {
  const name = feature?.properties?.shapeName || feature?.properties?.name || "";
  const selected = normalizeString(name) === normalizeString(props.regionSelectionnee);
  return styleForScore(getScore(name), selected);
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
  const totalLine = data
    ? `<div>${total} bénéficiaire${total > 1 ? "s" : ""}</div>`
    : "<div>Aucun bénéficiaire enregistré</div>";
  return `<strong>${display}</strong><div>${scoreLine}</div>${totalLine}`;
}

function onFeatureClick(event) {
  const layer = event.target;
  const propsData = layer?.feature?.properties;
  if (!propsData) return;
  const raw = propsData.shapeName || propsData.name || "";
  emit("region-selectionnee", displayName(raw));
}

function validCoordinates(zone) {
  const latRaw = zone?.latitude ?? zone?.lat;
  const lngRaw = zone?.longitude ?? zone?.lng;
  if (latRaw == null || lngRaw == null || String(latRaw).trim() === "" || String(lngRaw).trim() === "") return null;
  const lat = Number(latRaw);
  const lng = Number(lngRaw);
  return Number.isFinite(lat) && Number.isFinite(lng) && lat >= -90 && lat <= 90 && lng >= -180 && lng <= 180
    ? [lat, lng]
    : null;
}

function zoneColor(zone) {
  const score = Number(zone?.score_moyen ?? zone?.score);
  if (!Number.isFinite(score)) return "#64748b";
  if (score >= 80) return "#dc2626";
  if (score >= 60) return "#f97316";
  if (score >= 40) return "#eab308";
  return "#16a34a";
}

function addPopupLine(container, label, value) {
  const line = document.createElement("p");
  line.style.margin = "4px 0";
  const title = document.createElement("strong");
  title.textContent = `${label} : `;
  line.append(title, document.createTextNode(value || unavailable));
  container.append(line);
}

function popupForZone(zone) {
  const content = document.createElement("div");
  const title = document.createElement("strong");
  title.textContent = zone.nom || "Zone";
  content.append(title);

  const score = zone.score_moyen ?? zone.score;
  addPopupLine(content, "Score", score == null ? unavailable : `${score}/100`);
  addPopupLine(content, "Priorité", zone.priorite_ia || zone.priorite || zone.niveau);
  addPopupLine(content, "Bénéficiaires", zone.total_beneficiaires == null ? unavailable : String(zone.total_beneficiaires));
  addPopupLine(content, "Observation IA", zone.observation_ia || zone.observation);
  addPopupLine(content, "Recommandation", zone.recommandation_ia || zone.recommandation || zone.recommendation);
  return content;
}

function renderZoneMarkers() {
  if (!mapInstance) return;
  if (zoneMarkersLayer) mapInstance.removeLayer(zoneMarkersLayer);
  zoneMarkers.clear();
  zoneMarkersLayer = L.layerGroup();

  for (const zone of props.zones) {
    const coordinates = validCoordinates(zone);
    if (!coordinates || !zone.id) continue;
    const color = zoneColor(zone);
    const marker = L.circleMarker(coordinates, {
      radius: zone.id === props.zoneSelectionneeId ? 10 : 7,
      color: "#ffffff",
      weight: zone.id === props.zoneSelectionneeId ? 3 : 2,
      fillColor: color,
      fillOpacity: 0.95,
    });
    marker.bindTooltip(zone.nom || "Zone", { direction: "top", offset: [0, -7] });
    marker.bindPopup(popupForZone(zone));
    marker.on("click", () => emit("zone-selectionnee", zone));
    zoneMarkers.set(String(zone.id), marker);
    zoneMarkersLayer.addLayer(marker);
  }
  zoneMarkersLayer.addTo(mapInstance);
}

function focusZone(zoneId) {
  const marker = zoneMarkers.get(String(zoneId));
  if (!marker || !mapInstance) return;
  for (const [id, item] of zoneMarkers) {
    const zone = props.zones.find(entry => String(entry.id) === id);
    const color = zoneColor(zone);
    item.setRadius(id === String(zoneId) ? 10 : 7);
    item.setStyle({ weight: id === String(zoneId) ? 3 : 2, fillColor: color });
  }
  mapInstance.setView(marker.getLatLng(), Math.max(mapInstance.getZoom(), 9), { animate: true });
  marker.openPopup();
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
          layer.setStyle({ weight: 2.5, fillOpacity: 0.9 });
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
      layer.setStyle(styleForScore(getScore(name), true));
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
  renderZoneMarkers();
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
  () => props.zones,
  () => {
    renderZoneMarkers();
    if (props.zoneSelectionneeId) focusZone(props.zoneSelectionneeId);
  },
  { deep: true }
);

watch(
  () => props.zoneSelectionneeId,
  (zoneId) => {
    if (zoneId) focusZone(zoneId);
  }
);

watch(
  () => props.regionSelectionnee,
  () => highlightSelection()
);

onUnmounted(() => {
  if (mapInstance && geoJsonLayer) {
    mapInstance.removeLayer(geoJsonLayer);
  }
  if (mapInstance && zoneMarkersLayer) mapInstance.removeLayer(zoneMarkersLayer);
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
