<template>
  <div class="w-full h-full relative">
    <LMap
      ref="mapRef"
      :zoom="7"
      :center="[14.4974, -14.4524]"
      :min-zoom="7"
      :max-zoom="10"
      :max-bounds="senegalBounds"
      :max-bounds-viscosity="1"
      :use-global-leaflet="true"
    >
      <LTileLayer
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        layer-type="base"
        name="OpenStreetMap"
        attribution="&copy; OpenStreetMap contributors"
      />

      <!-- GeoJSON des régions du Sénégal colorées -->
      <LGeoJson
        v-if="geoJsonData"
        :geojson="geoJsonData"
        :options="geoJsonOptions"
      />

      <!-- Marqueurs pour chaque ONG -->
      <LMarker
        v-for="marker in markersWithOffset"
        :key="marker.ong.id"
        :lat-lng="marker.position"
        :icon="marker.icon"
      >
        <LPopup>
          <div class="text-sm min-w-[200px] p-1">
            <div class="font-bold text-bleu-nuit text-base mb-2">
              {{ marker.ong.name }}
            </div>
            <div class="text-slate-600 mb-2">
              <span class="font-medium">Région:</span> {{ marker.ong.region }}
            </div>
            <div class="text-slate-600 mb-2">
              <span class="font-medium">Projets:</span>
              {{ marker.ong.projets_count || 0 }}
            </div>
            <div class="text-slate-600 mb-3">
              <span class="font-medium">Campagnes actives:</span>
              {{ marker.ong.campagnes_count || 0 }}
            </div>
            <button
              class="w-full bg-bleu-nuit hover:bg-bleu-nuit/90 text-white font-medium py-2 px-4 rounded-lg transition-colors text-sm"
              @click="voirONG(marker.ong.id)"
            >
              Voir l'ONG
            </button>
          </div>
        </LPopup>
      </LMarker>
    </LMap>

    <!-- Compteur -->
    <div
      class="absolute top-4 right-4 bg-white/95 backdrop-blur-sm rounded-lg shadow-md px-3 py-2 z-[1000]"
    >
      <span class="text-sm font-semibold text-bleu-nuit"
        >{{ ongsAffichees.length }} ONG(s)</span
      >
    </div>

    <!-- Légende des régions (style image) -->
    <div
      class="absolute bottom-4 left-4 bg-white rounded-lg shadow-md p-3 z-[1000]"
      style="min-width: 140px; border: 1px solid #e2e8f0"
    >
      <div
        class="text-xs font-bold text-slate-700 mb-2 uppercase tracking-wide"
      >
        Régions
      </div>
      <div class="flex items-center gap-2 text-xs mb-1.5">
        <div
          class="w-4 h-4 rounded-sm flex-shrink-0"
          style="background-color: #021427"
        ></div>
        <span class="text-slate-700 font-medium">Avec ONG</span>
      </div>
      <div class="flex items-center gap-2 text-xs">
        <div
          class="w-4 h-4 rounded-sm flex-shrink-0"
          style="background-color: #e2e8f0; border: 1px solid #cbd5e1"
        ></div>
        <span class="text-slate-400">Sans ONG</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, ref } from "vue";
import { useRouter } from "vue-router";
import {
  LMap,
  LTileLayer,
  LMarker,
  LPopup,
  LGeoJson,
} from "@vue-leaflet/vue-leaflet";
import L from "leaflet";
import "leaflet/dist/leaflet.css";
import geoJsonSenegal from "@/data/senegal-regions.geojson?raw";

const router = useRouter();
const mapRef = ref(null);

const props = defineProps({
  ongs: { type: Array, default: () => [] },
  filtreRegion: { type: String, default: "toutes" },
  filtreDomaine: { type: String, default: "tous" },
});

// Limites du Sénégal (bounds pour bloquer la carte)
const senegalBounds = [
  [12.0, -17.5],
  [16.5, -11.5],
];

// Parser le GeoJSON
const geoJsonData = computed(() => {
  try {
    return JSON.parse(geoJsonSenegal);
  } catch (e) {
    console.error("Erreur parsing GeoJSON:", e);
    return null;
  }
});

// Coordonnées du centre de chaque région du Sénégal
const REGION_CENTERS = {
  dakar: [14.7167, -17.4677],
  diourbel: [14.65, -16.2333],
  fatick: [14.3333, -16.4167],
  kaffrine: [14.1086, -15.5058],
  kaolack: [14.1852, -16.2639],
  kédougou: [12.4833, -12.1667],
  kedougou: [12.4833, -12.1667],
  kolda: [12.8833, -14.95],
  louga: [15.6167, -16.3833],
  matam: [15.6556, -13.2553],
  "saint-louis": [16.0278, -16.5086],
  sédhiou: [12.7083, -15.5569],
  sedhiou: [12.7083, -15.5569],
  tambacounda: [13.7333, -13.6667],
  thiès: [14.7833, -16.95],
  thies: [14.7833, -16.95],
  ziguinchor: [12.5833, -16.2667],
};

// Fonction pour normaliser le nom de la région
const normalizeRegion = (name) => {
  if (!name) return "";
  return name
    .trim()
    .toLowerCase()
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "");
};

// Fonction pour obtenir les coordonnées du centre d'une région
const getRegionCenter = (regionName) => {
  if (!regionName) return [14.4974, -14.4524];

  const normalizedRegion = normalizeRegion(regionName);

  for (const [region, coords] of Object.entries(REGION_CENTERS)) {
    if (
      normalizedRegion === region ||
      normalizedRegion.includes(region) ||
      region.includes(normalizedRegion)
    ) {
      return coords;
    }
  }

  return [14.4974, -14.4524];
};

// Compter les ONGs par région
const getOngsInRegion = (regionName) => {
  if (!regionName || !props.ongs.length) return [];
  const normalizedRegion = normalizeRegion(regionName);

  return props.ongs.filter((ong) => {
    if (!ong.region) return false;
    const ongRegion = normalizeRegion(ong.region);
    return (
      ongRegion.includes(normalizedRegion) ||
      normalizedRegion.includes(ongRegion)
    );
  });
};

// Options GeoJSON pour le style et les événements
const geoJsonOptions = computed(() => ({
  style: (feature) => {
    const regionName = feature?.properties?.shapeName || "";
    const ongsInRegion = getOngsInRegion(regionName);
    const hasOng = ongsInRegion.length > 0;

    return {
      fillColor: hasOng ? "#021427" : "#e2e8f0",
      fillOpacity: 0.35,
      color: hasOng ? "#021427" : "#94a3b8",
      weight: hasOng ? 2 : 1,
    };
  },
  onEachFeature: (feature, layer) => {
    const regionName = feature?.properties?.shapeName || "";
    const ongsInRegion = getOngsInRegion(regionName);
    const count = ongsInRegion.length;

    // Tooltip avec le nom de la région et le nombre d'ONG
    layer.bindTooltip(`<strong>${regionName}</strong><br/>${count} ONG(s)`, {
      direction: "top",
      className: "region-tooltip",
    });

    // Au clic, zoomer sur la région
    layer.on("click", () => {
      const center = getRegionCenter(regionName);
      const map = mapRef.value?.leafletObject;
      if (map) {
        map.setView(center, 9, { animate: true });
      }
    });
  },
}));

// ONG filtrées
const ongsAffichees = computed(() => {
  let result = props.ongs;

  if (props.filtreRegion && props.filtreRegion !== "toutes") {
    result = result.filter(
      (ong) =>
        ong.region &&
        ong.region.toLowerCase().includes(props.filtreRegion.toLowerCase())
    );
  }

  if (props.filtreDomaine && props.filtreDomaine !== "tous") {
    result = result.filter(
      (ong) =>
        ong.intervention_domain &&
        ong.intervention_domain
          .toLowerCase()
          .includes(props.filtreDomaine.toLowerCase())
    );
  }

  return result;
});

// Marqueurs avec décalage pour éviter la superposition
const markersWithOffset = computed(() => {
  const regionGroups = {};
  const offsetRange = 0.015;

  ongsAffichees.value.forEach((ong) => {
    const region = ong.region || "AUTRE";
    if (!regionGroups[region]) {
      regionGroups[region] = [];
    }
    regionGroups[region].push(ong);
  });

  const markers = [];

  Object.entries(regionGroups).forEach(([region, ongsInRegion]) => {
    const baseCoords = getRegionCenter(region);
    const count = ongsInRegion.length;

    ongsInRegion.forEach((ong, index) => {
      let position;

      if (count === 1) {
        position = baseCoords;
      } else {
        const angle = (2 * Math.PI * index) / count;
        const radius = offsetRange * Math.sqrt(count);
        const latOffset = Math.cos(angle) * radius;
        const lngOffset = Math.sin(angle) * radius;

        position = [baseCoords[0] + latOffset, baseCoords[1] + lngOffset];
      }

      const iconHtml = `
        <div style="
          position: relative;
          width: 34px;
          height: 40px;
          display: flex;
          flex-direction: column;
          align-items: center;
        ">
          <!-- Pin body -->
          <div style="
            width: 34px;
            height: 34px;
            background: #744D03;
            border-radius: 50% 50% 50% 0;
            transform: rotate(-45deg);
            box-shadow: 0 3px 8px rgba(0,0,0,0.4);
            border: 2px solid #fff;
            display: flex;
            align-items: center;
            justify-content: center;
          ">
            <div style="transform: rotate(45deg);">
              <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#ffffff" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                <rect width="16" height="20" x="4" y="2" rx="2" ry="2"/>
                <path d="M9 22v-4h6v4"/>
                <path d="M8 6h.01"/><path d="M16 6h.01"/><path d="M12 6h.01"/>
                <path d="M12 10h.01"/><path d="M12 14h.01"/>
                <path d="M16 10h.01"/><path d="M16 14h.01"/>
                <path d="M8 10h.01"/><path d="M8 14h.01"/>
              </svg>
            </div>
          </div>
          <!-- Pin tip -->
          <div style="
            width: 0; height: 0;
            border-left: 5px solid transparent;
            border-right: 5px solid transparent;
            border-top: 8px solid #744D03;
            margin-top: -2px;
          "></div>
        </div>
      `;

      const customIcon = L.divIcon({
        className: "building-marker",
        html: iconHtml,
        iconSize: [34, 42],
        iconAnchor: [17, 42],
      });

      markers.push({
        ong,
        position,
        icon: customIcon,
      });
    });
  });

  return markers;
});

// Fonction pour voir les détails de l'ONG
const voirONG = (id) => {
  router.push(`/super-admin/ongs?id=${id}`);
};
</script>

<style scoped>
:deep(.leaflet-container) {
  height: 100%;
  width: 100%;
  border-radius: 0.75rem;
}

:deep(.leaflet-popup-content-wrapper) {
  border-radius: 0.5rem;
  padding: 8px;
}

:deep(.leaflet-popup-content) {
  margin: 0;
}

:deep(.building-marker) {
  background: transparent !important;
  border: none !important;
}

:deep(.leaflet-marker-icon) {
  margin: 0 !important;
}

:deep(.region-tooltip) {
  background: white;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1);
  padding: 6px 10px;
}
</style>