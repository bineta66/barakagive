<template>
  <router-view />
</template>

<script setup>
import { ref, onMounted, onUnmounted, provide } from "vue";
import { offlineStorage } from "@/services/offlineStorage";
import { useBeneficiaryStore } from "@/stores/beneficiary";

// ── État global de la connexion ─────────────────────────────────────────────
const connectionStatus = ref(typeof navigator === "undefined" || navigator.onLine ? "online" : "offline");
let connectivityProbe = null;
let connectivityInterval = null;
let connectivityCheckRunning = false;

// ── Statistiques de sync (partagées dans toute l'app) ──────────────────────
const syncStats = ref({
  pending: 0,
  syncing: 0,
  synced: 0,
  failed: 0,
  conflict: 0,
  total: 0,
});
const lastSyncTime = ref(null);

// Disponible dans toute l'application via inject()
provide("connectionStatus", connectionStatus);
provide("syncStats", syncStats);
provide("lastSyncTime", lastSyncTime);

// ── Mise à jour des stats locales ───────────────────────────────────────────
const refreshSyncStats = async () => {
  try {
    syncStats.value = await offlineStorage.getStats();
  } catch {
    // Silencieux
  }
};

// ── Synchronisation automatique ─────────────────────────────────────────────
const triggerAutoSync = async () => {
  try {
    const pending = await offlineStorage.getPendingBeneficiaries();
    if (pending.length === 0) {
      await refreshSyncStats();
      return;
    }

    const store = useBeneficiaryStore();
    await store.syncOfflineBeneficiaries();
    await refreshSyncStats();
    lastSyncTime.value = new Date();
  } catch (error) {
    console.error("[BarakaGive] Erreur de synchronisation automatique :", error);
  }
};

// ── Gestionnaires d'événements navigateur ────────────────────────────────────
const onOffline = () => {
  connectivityProbe?.abort();
  connectionStatus.value = "offline";
};

const checkInternetConnection = async () => {
  if (typeof navigator === "undefined" || !navigator.onLine) {
    onOffline();
    return;
  }
  if (connectivityCheckRunning) return;

  connectivityCheckRunning = true;
  const controller = new AbortController();
  connectivityProbe = controller;
  const timeout = window.setTimeout(() => controller.abort(), 3000);
  try {
    // navigator.onLine ne distingue pas toujours le réseau local d'un accès
    // Internet fonctionnel. Une requête sans données vérifie l'accès réseau réel.
    await fetch("https://www.google.com/generate_204", {
      method: "GET",
      mode: "no-cors",
      cache: "no-store",
      signal: controller.signal,
    });
    if (!controller.signal.aborted && navigator.onLine) {
      const wasOffline = connectionStatus.value === "offline";
      connectionStatus.value = "online";
      if (wasOffline) await triggerAutoSync();
    }
  } catch {
    if (navigator.onLine) {
      connectionStatus.value = "offline";
    }
  } finally {
    window.clearTimeout(timeout);
    if (connectivityProbe === controller) connectivityProbe = null;
    connectivityCheckRunning = false;
  }
};

const onOnline = () => {
  void checkInternetConnection();
};

const onVisibilityChange = () => {
  if (document.visibilityState === "visible") void checkInternetConnection();
};

/*
 * An online event only means the browser has a network interface. Probe
 * periodically too, because a router can remain connected without Internet.
 */
const startConnectivityMonitoring = () => {
  void checkInternetConnection();
  connectivityInterval = window.setInterval(checkInternetConnection, 15000);
};

// ── Lifecycle ───────────────────────────────────────────────────────────────
onMounted(async () => {
  connectionStatus.value = typeof navigator === "undefined" || navigator.onLine ? "online" : "offline";
  window.addEventListener("online", onOnline);
  window.addEventListener("offline", onOffline);
  document.addEventListener("visibilitychange", onVisibilityChange);
  startConnectivityMonitoring();
  await refreshSyncStats();
});

onUnmounted(() => {
  window.removeEventListener("online", onOnline);
  window.removeEventListener("offline", onOffline);
  document.removeEventListener("visibilitychange", onVisibilityChange);
  if (connectivityInterval) window.clearInterval(connectivityInterval);
  connectivityProbe?.abort();
});
</script>

<style>
html,
body,
#app {
  width: 100%;
  height: 100%;
  margin: 0;
  padding: 0;
}
</style>
