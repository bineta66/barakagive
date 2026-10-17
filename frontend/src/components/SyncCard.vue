<template>
  <div
    class="rounded-2xl border p-4 transition-all"
    :class="cardClass"
  >
    <div class="flex items-center justify-between">
      <div class="flex items-center gap-3">
        <!-- Icône -->
        <div
          class="w-11 h-11 rounded-xl flex items-center justify-center"
          :class="iconClass"
        >
          <Wifi v-if="status === 'online'" :size="22" />
          <WifiOff v-else-if="status === 'offline'" :size="22" />
          <Loader2
            v-else-if="status === 'syncing'"
            :size="22"
            class="animate-spin"
          />
          <CheckCircle v-else-if="status === 'success'" :size="22" />
          <AlertCircle v-else :size="22" />
        </div>

        <!-- Texte -->
        <div>
          <h3 class="font-bold" :class="titleClass">
            {{ title }}
          </h3>
          <p class="text-xs text-slate-600">
            {{ subtitle }}
          </p>
        </div>
      </div>

      <!-- Heure -->
      <div
        v-if="lastSync"
        class="text-xs text-slate-500"
      >
        {{ lastSync }}
      </div>
    </div>

    <!-- Statistiques -->
    <div
      v-if="showStats && (stats.total > 0 || totalItems > 0)"
      class="grid grid-cols-2 gap-3 mt-4 pt-4 border-t sm:grid-cols-4"
    >
      <div class="text-center">
        <p class="text-lg font-bold text-bleu-nuit">
          {{ stats.pending ?? stats.enAttente ?? 0 }}
        </p>
        <p class="text-[11px] text-slate-500">
          Attente
        </p>
      </div>

      <div class="text-center">
        <p class="text-lg font-bold text-bleu-accent">
          {{ stats.syncing ?? stats.enCours ?? 0 }}
        </p>
        <p class="text-[11px] text-slate-500">
          Envoi
        </p>
      </div>

      <div class="text-center">
        <p class="text-lg font-bold text-bleu-accent">
          {{ stats.synced ?? stats.synchronises ?? 0 }}
        </p>
        <p class="text-[11px] text-slate-500">
          Sync
        </p>
      </div>

      <div class="text-center">
        <p class="text-lg font-bold text-rose-baraka">
          {{ (stats.failed ?? 0) + (stats.conflict ?? 0) + (stats.echecs ?? 0) }}
        </p>
        <p class="text-[11px] text-slate-500">
          Erreurs
        </p>
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

const props = defineProps({
  showStats: {
    type: Boolean,
    default: false,
  },
});

// État global fourni par App.vue
const connectionStatus = inject("connectionStatus", ref("online"));

// Statistiques injectées depuis useSync
const syncStats = inject(
  "syncStats",
  ref({
    pending: 0,
    syncing: 0,
    synced: 0,
    failed: 0,
    conflict: 0,
    total: 0,
  })
);

const lastSyncTime = inject("lastSyncTime", ref(null));

const totalItems = computed(() => {
  const s = syncStats.value;
  return s.total ?? ((s.pending || 0) + (s.syncing || 0) + (s.synced || 0) + (s.failed || 0) + (s.conflict || 0));
});

// Détermination du statut
const status = computed(() => {
  if (connectionStatus.value === "offline") return "offline";
  const inSync = (syncStats.value.syncing ?? syncStats.value.enCours ?? 0) > 0;
  const inError = ((syncStats.value.failed ?? 0) + (syncStats.value.conflict ?? 0) + (syncStats.value.echecs ?? 0)) > 0;
  const isPending = (syncStats.value.pending ?? syncStats.value.enAttente ?? 0) > 0;
  if (inSync) return "syncing";
  if (inError) return "error";
  if (!isPending) return "success";
  return "online";
});

const stats = computed(() => syncStats.value);

const title = computed(() => {
  switch (status.value) {
    case "offline":
      return "Hors connexion";
    case "syncing":
      return "Synchronisation en cours";
    case "success":
      return "Synchronisé";
    case "error":
      return "Erreur de synchronisation";
    default:
      return "En ligne";
  }
});

const subtitle = computed(() => {
  switch (status.value) {
    case "offline":
      return "Les données sont enregistrées localement.";
    case "syncing":
      return `${stats.value.enCours} formulaire(s) en cours d'envoi.`;
    case "success":
      return "Toutes les données sont synchronisées.";
    case "error":
      return `${stats.value.echecs} formulaire(s) en échec.`;
    default:
      return "Les nouveaux formulaires seront envoyés automatiquement.";
  }
});

const cardClass = computed(() => {
  switch (status.value) {
    case "offline":
      return "bg-rose-baraka/10 border-rose-baraka/20";
    case "syncing":
      return "bg-bleu-accent/10 border-bleu-accent/20";
    case "success":
      return "bg-bleu-accent/10 border-bleu-accent/20";
    case "error":
      return "bg-rose-baraka/10 border-rose-baraka/20";
    default:
      return "bg-white border-slate-200";
  }
});

const iconClass = computed(() => {
  switch (status.value) {
    case "offline":
      return "bg-rose-baraka/10 text-rose-baraka";
    case "syncing":
      return "bg-bleu-accent/10 text-bleu-accent";
    case "success":
      return "bg-bleu-accent/10 text-bleu-accent";
    case "error":
      return "bg-rose-baraka/10 text-rose-baraka";
    default:
      return "bg-bleu-accent/10 text-bleu-accent";
  }
});

const titleClass = computed(() => {
  switch (status.value) {
    case "offline":
      return "text-rose-baraka";
    case "syncing":
      return "text-or";
    case "success":
      return "text-bleu-accent";
    case "error":
      return "text-rose-baraka";
    default:
      return "text-bleu-accent";
  }
});

const lastSync = computed(() => {
  if (!lastSyncTime.value) return "";

  const diff = Math.floor(
    (Date.now() - new Date(lastSyncTime.value)) / 60000
  );

  if (diff < 1) return "À l'instant";
  if (diff < 60) return `Il y a ${diff} min`;

  const h = Math.floor(diff / 60);
  return `Il y a ${h} h`;
});
</script>

<style scoped>
.rounded-2xl {
  backdrop-filter: blur(10px);
}
</style>
