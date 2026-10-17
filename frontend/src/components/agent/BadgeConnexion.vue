<template>
  <button
    type="button"
    class="agent-badge-connexion"
    :class="[
      isOnline ? 'badge--online' : 'badge--offline',
      toggleForcedOffline ? 'badge--clickable' : ''
    ]"
    :title="badgeTitle"
    @click="handleClick"
  >
    <!-- Point de statut animé -->
    <span class="badge__dot" :class="isOnline ? 'dot--online' : 'dot--offline'" />

    <!-- Icône -->
    <component :is="isOnline ? Wifi : WifiOff" :size="13" />

    <!-- Texte -->
    <span class="badge__label">{{ labelText }}</span>
  </button>
</template>

<script setup>
import { inject, computed, ref } from "vue";
import { Wifi, WifiOff } from "lucide-vue-next";

const connectionStatus = inject("connectionStatus", ref("offline"));
const forcedOffline = inject("forcedOffline", ref(false));
const toggleForcedOffline = inject("toggleForcedOffline", null);

const isOnline = computed(() => connectionStatus.value === "online");
const isForced = computed(() => forcedOffline.value);

const labelText = computed(() => {
  if (isOnline.value) return "En ligne";
  return isForced.value ? "Hors connexion (test)" : "Hors connexion";
});

const badgeTitle = computed(() => {
  if (!toggleForcedOffline) return isOnline.value ? "En ligne" : "Hors connexion";
  return isForced.value
    ? "Mode hors ligne forcé pour test (cliquez pour rétablir la connexion)"
    : "Cliquez pour simuler le mode hors connexion (test terrain)";
});

const handleClick = () => {
  if (toggleForcedOffline) {
    toggleForcedOffline();
  }
};
</script>

<style scoped>
.agent-badge-connexion {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 6px 14px;
  border-radius: 999px;
  font-size: 12px;
  font-weight: 700;
  border: 1.5px solid transparent;
  backdrop-filter: blur(8px);
  transition: all 0.3s ease;
  letter-spacing: 0.01em;
  white-space: nowrap;
  background: transparent;
  font-family: inherit;
}

.badge--clickable {
  cursor: pointer;
  user-select: none;
}

.badge--clickable:hover {
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

.badge--online {
  background: rgba(16, 185, 129, 0.1);
  border-color: rgba(16, 185, 129, 0.3);
  color: #047857;
}

.badge--offline {
  background: rgba(239, 68, 68, 0.1);
  border-color: rgba(239, 68, 68, 0.3);
  color: #b91c1c;
}

.badge__dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  flex-shrink: 0;
}

.dot--online {
  background: #10b981;
  animation: pulse-green 2s infinite;
}

.dot--offline {
  background: #ef4444;
}

.badge__label {
  line-height: 1;
}

@keyframes pulse-green {
  0%, 100% { opacity: 1; box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.4); }
  50% { opacity: 0.8; box-shadow: 0 0 0 4px rgba(16, 185, 129, 0); }
}
</style>
