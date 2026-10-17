import { ref, inject, watch, onMounted, onUnmounted } from "vue";
import api from "@/services/api";
import { offlineStorage } from "@/services/offlineStorage";

/**
 * useSync — Gestion de la synchronisation automatique des bénéficiaires hors ligne
 *
 * Flux de sync pour chaque item PENDING :
 *   1. PENDING → SYNCING
 *   2. POST /api/beneficiaries/pwa-sync/
 *   3. Succès → SYNCED
 *      Doublon → CONFLICT
 *      Erreur  → FAILED
 *
 * La sync se déclenche automatiquement dès que la connexion revient.
 * Aucune interaction utilisateur n'est requise.
 */

export const SYNC_STATUS = {
  PENDING: "PENDING",
  SYNCING: "SYNCING",
  SYNCED: "SYNCED",
  FAILED: "FAILED",
  CONFLICT: "CONFLICT",
};

export function useSync() {
  const connectionStatus = inject("connectionStatus", ref("offline"));
  const syncStatsProvided = inject("syncStats", null);

  const isSyncing = ref(false);
  const lastSyncTime = ref(null);
  const syncError = ref(null);
  const localStats = ref({
    pending: 0,
    syncing: 0,
    synced: 0,
    failed: 0,
    conflict: 0,
    total: 0,
  });

  let retryTimeout = null;
  const RETRY_DELAY = 30_000;

  // ── Mise à jour des statistiques locales ──────────────────────────────────
  const updateStats = async () => {
    const stats = await offlineStorage.getStats();
    localStats.value = stats;

    // Propager vers App.vue si les stats globales sont accessibles
    if (syncStatsProvided) {
      syncStatsProvided.value = stats;
    }
  };

  // ── Synchroniser un seul item ─────────────────────────────────────────────
  const syncOneItem = async (item) => {
    // 1. Marquer SYNCING
    await offlineStorage.updateStatus(item.local_id, "SYNCING");

    const payload = {
      local_id: item.local_id,
      campagne_id: item.campagne_id,
      zone_id: item.zone_id,
      formulaire_id: item.formulaire_id,
      beneficiary: item.beneficiary,
      responses: item.responses || [],
    };

    try {
      const { data } = await api.post("/api/beneficiaries/pwa-sync/", payload);

      // 2. Succès → SYNCED
      await offlineStorage.updateStatus(item.local_id, "SYNCED", {
        server_id: data?.id || null,
        error_message: null,
      });

      return { status: "SYNCED", local_id: item.local_id };
    } catch (error) {
      // Extraire le message d'erreur précis renvoyé par Django
      let errorMsg = "Erreur inconnue";
      if (error.response?.data?.detail) {
        errorMsg = error.response.data.detail;
      } else if (error.response?.data?.beneficiary) {
        const bErr = error.response.data.beneficiary;
        errorMsg = Object.entries(bErr)
          .map(([k, v]) => `${k}: ${Array.isArray(v) ? v.join(", ") : v}`)
          .join(" | ");
      } else if (error.response?.data && typeof error.response.data === "object") {
        errorMsg = Object.entries(error.response.data)
          .map(([k, v]) => `${k}: ${Array.isArray(v) ? v.join(", ") : v}`)
          .join(" | ");
      } else if (error.message) {
        errorMsg = error.message;
      }

      // 3. Doublon → CONFLICT
      if (error.response?.status === 409) {
        await offlineStorage.updateStatus(item.local_id, "CONFLICT", {
          error_message: errorMsg || "Doublon détecté côté serveur.",
        });
        return { status: "CONFLICT", local_id: item.local_id, error: errorMsg };
      }

      // 4. Autre erreur → FAILED
      await offlineStorage.updateStatus(item.local_id, "FAILED", {
        error_message: errorMsg,
      });
      return { status: "FAILED", local_id: item.local_id, error: errorMsg };
    }
  };

  // ── Synchroniser tous les items PENDING / FAILED ─────────────────────────
  const syncAll = async (includeFailed = true) => {
    if (isSyncing.value) return { synced: 0, failed: 0, conflict: 0 };
    if (connectionStatus.value !== "online") return { synced: 0, failed: 0, conflict: 0 };

    const pending = await offlineStorage.getPendingBeneficiaries(includeFailed);
    if (pending.length === 0) {
      await updateStats();
      return { synced: 0, failed: 0, conflict: 0 };
    }

    isSyncing.value = true;
    syncError.value = null;

    let synced = 0;
    let failed = 0;
    let conflict = 0;

    try {
      for (const item of pending) {
        const result = await syncOneItem(item);
        if (result.status === "SYNCED") synced++;
        else if (result.status === "CONFLICT") conflict++;
        else failed++;

        // Mettre à jour les stats après chaque item
        await updateStats();
      }

      lastSyncTime.value = new Date();

      return { synced, failed, conflict };
    } finally {
      isSyncing.value = false;
      await updateStats();
    }
  };

  // ── Retry automatique après 30s en cas d'erreur ───────────────────────────
  const scheduleRetry = () => {
    if (retryTimeout) clearTimeout(retryTimeout);
    retryTimeout = setTimeout(async () => {
      if (connectionStatus.value === "online") {
        await syncAll();
      }
    }, RETRY_DELAY);
  };

  // ── Réagir aux changements de connexion ───────────────────────────────────
  watch(connectionStatus, async (status) => {
    if (status === "online") {
      const stats = await offlineStorage.getStats();
      if (stats.pending > 0 || stats.failed > 0) {
        await syncAll();
      }
    } else {
      if (retryTimeout) {
        clearTimeout(retryTimeout);
        retryTimeout = null;
      }
    }
  });

  // ── Initialisation ────────────────────────────────────────────────────────
  onMounted(async () => {
    await updateStats();

    if (connectionStatus.value === "online" && localStats.value.pending > 0) {
      await syncAll();
    }
  });

  onUnmounted(() => {
    if (retryTimeout) clearTimeout(retryTimeout);
  });

  return {
    isSyncing,
    localStats,
    lastSyncTime,
    syncError,
    syncAll,
    updateStats,
    SYNC_STATUS,
  };
}