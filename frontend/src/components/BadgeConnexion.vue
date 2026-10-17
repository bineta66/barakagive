<template>
  <button
    type="button"
    class="inline-flex items-center gap-2 px-3 py-1 rounded-full text-xs font-semibold border transition-all duration-300 cursor-pointer select-none"
    :class="
      isOnline
        ? 'bg-[#f0fdf4] border-[#86efac] text-[#15803d]'
        : 'bg-[#fef2f2] border-[#fca5a5] text-[#dc2626]'
    "
    :title="isForced ? 'Mode hors-ligne simulé (cliquez pour rétablir)' : 'Cliquez pour basculer en mode hors connexion pour tester'"
    @click="handleClick"
  >
    <!-- Point de connexion -->
    <span
      class="w-2 h-2 rounded-full flex-shrink-0"
      :class="
        isOnline
          ? 'bg-[#22c55e] animate-pulse'
          : 'bg-[#ef4444]'
      "
    ></span>

    <!-- Texte -->
    <span>{{ isOnline ? "En ligne" : (isForced ? "Hors connexion (test)" : "Hors connexion") }}</span>
  </button>
</template>

<script setup>
import { inject, computed, ref } from "vue";

// État global fourni par App.vue
const connectionStatus = inject("connectionStatus", ref("offline"));
const forcedOffline = inject("forcedOffline", ref(false));
const toggleForcedOffline = inject("toggleForcedOffline", null);

// Conversion en booléen
const isOnline = computed(() => connectionStatus.value === "online");
const isForced = computed(() => forcedOffline.value);

const handleClick = () => {
  if (toggleForcedOffline) toggleForcedOffline();
};
</script>

<style scoped>
div {
  backdrop-filter: blur(10px);
}
</style>