import { inject, computed, ref } from "vue";

/** Expose l'état réseau natif fourni par App.vue. */
export function useOnlineStatus() {
  const initialStatus = typeof navigator === "undefined" || navigator.onLine ? "online" : "offline";
  const connectionStatus = inject("connectionStatus", ref(initialStatus));

  const isOnline = computed(() => connectionStatus.value === "online");
  const isOffline = computed(() => connectionStatus.value === "offline");

  const statusLabel = computed(() =>
    isOnline.value ? "En ligne" : "Hors connexion"
  );

  // Classes CSS prêtes à l'emploi
  const badgeClass = computed(() =>
    isOnline.value
      ? "bg-emerald-50 border-emerald-200 text-emerald-700"
      : "bg-red-50 border-red-200 text-red-700"
  );

  const dotClass = computed(() =>
    isOnline.value
      ? "bg-emerald-500 animate-pulse"
      : "bg-red-500"
  );

  return {
    isOnline,
    isOffline,
    connectionStatus,
    statusLabel,
    badgeClass,
    dotClass,
  };
}
