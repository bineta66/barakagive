<template>
  <div class="sync-card" :class="cardTheme.bg">
    <!-- Ligne principale -->
    <div class="sync-card__header">
      <!-- Icône + Texte -->
      <div class="sync-card__left">
        <div class="sync-card__icon" :class="cardTheme.icon">
          <Wifi v-if="currentStatus === 'online'" :size="20" />
          <WifiOff v-else-if="currentStatus === 'offline'" :size="20" />
          <Loader2
            v-else-if="currentStatus === 'syncing'"
            :size="20"
            class="animate-spin"
          />
          <CheckCircle v-else-if="currentStatus === 'synced'" :size="20" />
          <AlertCircle v-else :size="20" />
        </div>

        <div>
          <h3 class="sync-card__title" :class="cardTheme.title">
            {{ cardTitle }}
          </h3>
          <p class="sync-card__subtitle">
            {{ cardSubtitle }}
          </p>
        </div>
      </div>

      <!-- Heure dernière sync -->
      <div v-if="lastSyncLabel" class="sync-card__time">
        {{ lastSyncLabel }}
      </div>
    </div>

    <!-- Statistiques (optionnel) -->
    <div v-if="showStats && stats.total > 0" class="sync-card__stats">
      <div class="sync-stat">
        <span class="sync-stat__value sync-stat__value--pending">
          {{ stats.pending }}
        </span>
        <span class="sync-stat__label">Attente</span>
      </div>
      <div class="sync-stat">
        <span class="sync-stat__value sync-stat__value--syncing">
          {{ stats.syncing }}
        </span>
        <span class="sync-stat__label">Envoi</span>
      </div>
      <div class="sync-stat">
        <span class="sync-stat__value sync-stat__value--synced">
          {{ stats.synced }}
        </span>
        <span class="sync-stat__label">Sync</span>
      </div>
      <div class="sync-stat">
        <span class="sync-stat__value sync-stat__value--failed">
          {{ stats.failed + stats.conflict }}
        </span>
        <span class="sync-stat__label">Erreurs</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { inject, computed, ref } from "vue";
import {
  Wifi,
  WifiOff,
  Loader2,
  CheckCircle,
  AlertCircle,
} from "lucide-vue-next";

defineProps({
  showStats: {
    type: Boolean,
    default: false,
  },
});

// État global fourni par App.vue
const connectionStatus = inject("connectionStatus", ref("offline"));
const syncStatsRaw = inject("syncStats", ref({
  pending: 0, syncing: 0, synced: 0, failed: 0, conflict: 0, total: 0,
}));
const lastSyncTime = inject("lastSyncTime", ref(null));

const stats = computed(() => syncStatsRaw.value);

// ── Statut courant ──────────────────────────────────────────────────────────
const currentStatus = computed(() => {
  if (connectionStatus.value === "offline") return "offline";
  if (stats.value.syncing > 0) return "syncing";
  if (stats.value.failed > 0 || stats.value.conflict > 0) return "error";
  if (stats.value.pending === 0 && stats.value.total > 0) return "synced";
  return "online";
});

// ── Thèmes visuels ──────────────────────────────────────────────────────────
const THEMES = {
  offline: {
    bg: "sync-card--offline",
    icon: "sync-card__icon--offline",
    title: "sync-card__title--offline",
  },
  syncing: {
    bg: "sync-card--syncing",
    icon: "sync-card__icon--syncing",
    title: "sync-card__title--syncing",
  },
  error: {
    bg: "sync-card--error",
    icon: "sync-card__icon--error",
    title: "sync-card__title--error",
  },
  synced: {
    bg: "sync-card--synced",
    icon: "sync-card__icon--synced",
    title: "sync-card__title--synced",
  },
  online: {
    bg: "sync-card--online",
    icon: "sync-card__icon--online",
    title: "sync-card__title--online",
  },
};

const cardTheme = computed(() => THEMES[currentStatus.value] || THEMES.online);

const cardTitle = computed(() => {
  switch (currentStatus.value) {
    case "offline": return "Hors connexion";
    case "syncing": return "Synchronisation en cours…";
    case "error": return "Erreur de synchronisation";
    case "synced": return "Tout est synchronisé";
    default: return "Connexion active";
  }
});

const cardSubtitle = computed(() => {
  switch (currentStatus.value) {
    case "offline": return "Les données sont enregistrées localement sur cet appareil.";
    case "syncing": return `${stats.value.syncing} formulaire(s) en cours d'envoi…`;
    case "error":
      return `${stats.value.failed + stats.value.conflict} formulaire(s) en échec ou en conflit.`;
    case "synced": return "Toutes les données ont été envoyées au serveur.";
    default: return stats.value.pending > 0
      ? `${stats.value.pending} formulaire(s) en attente d'envoi.`
      : "Les nouveaux formulaires seront envoyés automatiquement.";
  }
});

// ── Heure de la dernière sync ───────────────────────────────────────────────
const lastSyncLabel = computed(() => {
  if (!lastSyncTime.value) return "";
  const diff = Math.floor((Date.now() - new Date(lastSyncTime.value)) / 60000);
  if (diff < 1) return "À l'instant";
  if (diff < 60) return `Il y a ${diff} min`;
  return `Il y a ${Math.floor(diff / 60)} h`;
});
</script>

<style scoped>
.sync-card {
  border-radius: 16px;
  border: 1.5px solid transparent;
  padding: 16px;
  transition: all 0.3s ease;
  backdrop-filter: blur(8px);
}

/* États */
.sync-card--online    { background: #fff; border-color: #e2e8f0; }
.sync-card--offline   { background: rgba(254,242,242,0.9); border-color: #fecaca; }
.sync-card--syncing   { background: rgba(239,246,255,0.9); border-color: #bfdbfe; }
.sync-card--error     { background: rgba(254,242,242,0.9); border-color: #fca5a5; }
.sync-card--synced    { background: rgba(240,253,244,0.9); border-color: #86efac; }

/* Header */
.sync-card__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.sync-card__left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.sync-card__icon {
  width: 44px;
  height: 44px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}
.sync-card__icon--online  { background: #dcfce7; color: #15803d; }
.sync-card__icon--offline { background: #fee2e2; color: #dc2626; }
.sync-card__icon--syncing { background: #dbeafe; color: #1d4ed8; }
.sync-card__icon--error   { background: #fee2e2; color: #dc2626; }
.sync-card__icon--synced  { background: #dcfce7; color: #15803d; }

.sync-card__title {
  font-size: 14px;
  font-weight: 700;
  margin: 0;
}
.sync-card__title--online  { color: #15803d; }
.sync-card__title--offline { color: #dc2626; }
.sync-card__title--syncing { color: #1d4ed8; }
.sync-card__title--error   { color: #dc2626; }
.sync-card__title--synced  { color: #15803d; }

.sync-card__subtitle {
  font-size: 12px;
  color: #64748b;
  margin: 2px 0 0;
}

.sync-card__time {
  font-size: 11px;
  color: #94a3b8;
  white-space: nowrap;
}

/* Statistiques */
.sync-card__stats {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 8px;
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid rgba(0, 0, 0, 0.06);
}

@media (min-width: 480px) {
  .sync-card__stats {
    grid-template-columns: repeat(4, minmax(0, 1fr));
  }
}

.sync-stat {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2px;
}

.sync-stat__value {
  font-size: 20px;
  font-weight: 800;
  line-height: 1;
}
.sync-stat__value--pending  { color: #d97706; }
.sync-stat__value--syncing  { color: #2563eb; }
.sync-stat__value--synced   { color: #16a34a; }
.sync-stat__value--failed   { color: #dc2626; }

.sync-stat__label {
  font-size: 10px;
  color: #94a3b8;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}
</style>
