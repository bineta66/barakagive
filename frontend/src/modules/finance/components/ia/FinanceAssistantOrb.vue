<template>
  <button
    type="button"
    @click="handleClick"
    title="Orb Assistant IA Finance"
    aria-label="Ouvrir l'Orb Assistant IA Finance"
    class="fixed bottom-24 lg:bottom-6 right-4 sm:right-6 z-40 focus:outline-none group"
  >
    <!-- Anneau pulse animé (si ORANGE ou RED) -->
    <span
      v-if="isPulseAlert"
      class="absolute -inset-1.5 rounded-full animate-ping opacity-75 pointer-events-none"
      :class="ringPulseClass"
    />

    <!-- Halo lumineux autour de l'orbe (glow effect) -->
    <span
      class="absolute -inset-1 rounded-full blur-md opacity-70 transition-all duration-500"
      :class="glowClass"
    />

    <!-- Corps principal de l'orbe -->
    <div
      class="relative w-16 h-16 rounded-full flex items-center justify-center border-2 transition-all duration-500 ease-out group-hover:scale-110"
      :class="[orbBodyClass, isPulseAlert ? 'animate-pulse' : '']"
    >
      <!-- Reflet verre supérieur -->
      <span
        class="absolute top-1 left-1/2 -translate-x-1/2 w-8 h-3 rounded-full bg-white/25 blur-[1px] pointer-events-none"
      />

      <!-- Icône Finance / Sparkles -->
      <span class="relative z-10 flex items-center justify-center">
        <svg
          xmlns="http://www.w3.org/2000/svg"
          width="28"
          height="28"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="1.8"
          stroke-linecap="round"
          stroke-linejoin="round"
          class="text-white drop-shadow transition-transform duration-300 group-hover:scale-110"
        >
          <path d="M12 2v20M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6" />
        </svg>

        <!-- Étincelle IA -->
        <svg
          xmlns="http://www.w3.org/2000/svg"
          width="13"
          height="13"
          viewBox="0 0 24 24"
          fill="currentColor"
          class="absolute -top-2.5 -right-2.5 text-amber-300 drop-shadow animate-spin"
          style="animation-duration: 5s"
        >
          <path d="M12 2l2.4 5.6L20 10l-5.6 2.4L12 18l-2.4-5.6L4 10l5.6-2.4z" />
        </svg>
      </span>

      <!-- Badge alerte (Niveau de couleur) -->
      <span
        class="absolute -top-0.5 -right-0.5 w-5 h-5 rounded-full border-2 border-white flex items-center justify-center text-[10px] font-black text-white shadow-sm"
        :class="badgeBgClass"
      >
        {{ alertBadgeText }}
      </span>
    </div>
  </button>
</template>

<script setup>
import { computed, onMounted, onUnmounted } from "vue";
import { useFinanceAssistantStore } from "@/stores/financeAssistant.js";

const store = useFinanceAssistantStore();

let refreshInterval = null;

onMounted(() => {
  // Charger immédiatement
  store.fetchHomeData();
  // Rafraîchir toutes les 2 minutes pour garder la couleur à jour
  refreshInterval = setInterval(() => {
    store.fetchHomeData();
  }, 2 * 60 * 1000);
});

onUnmounted(() => {
  if (refreshInterval) clearInterval(refreshInterval);
});

const isPulseAlert = computed(
  () => store.alertLevel === "ORANGE" || store.alertLevel === "RED"
);

// ── Corps de l'orbe ─────────────────────────────────────────────
const orbBodyClass = computed(() => {
  switch (store.alertLevel) {
    case "RED":
      return "bg-gradient-to-br from-rose-baraka via-[#b00a42] to-bleu-nuit border-rose-baraka/80";
    case "ORANGE":
      return "bg-gradient-to-br from-rose-baraka/80 via-rose-baraka to-bleu-nuit border-rose-baraka/60";
    case "YELLOW":
      return "bg-gradient-to-br from-bleu-accent via-[#155a8e] to-bleu-nuit border-bleu-accent/80";
    default:
      return "bg-gradient-to-br from-bleu-accent via-[#104b78] to-bleu-nuit border-bleu-accent/80";
  }
});

// ── Halo Glow ──────────────────────────────────────────────────
const glowClass = computed(() => {
  switch (store.alertLevel) {
    case "RED":
      return "bg-rose-baraka";
    case "ORANGE":
      return "bg-rose-baraka/80";
    case "YELLOW":
      return "bg-bleu-accent";
    default:
      return "bg-bleu-accent";
  }
});

// ── Anneau pulse ────────────────────────────────────────────────
const ringPulseClass = computed(() => {
  switch (store.alertLevel) {
    case "RED":
      return "bg-rose-baraka/60";
    case "ORANGE":
      return "bg-rose-baraka/40";
    default:
      return "";
  }
});

// ── Badge ──────────────────────────────────────────────────────
const badgeBgClass = computed(() => {
  switch (store.alertLevel) {
    case "RED":
      return "bg-rose-baraka";
    case "ORANGE":
      return "bg-rose-baraka";
    case "YELLOW":
      return "bg-bleu-accent";
    default:
      return "bg-bleu-accent";
  }
});

const alertBadgeText = computed(() => {
  switch (store.alertLevel) {
    case "RED":
      return "!";
    case "ORANGE":
      return "!";
    case "YELLOW":
      return "•";
    default:
      return "✓";
  }
});

// ── Clic : ouvrir l'assistant ──────────────────────────────────
const handleClick = () => {
  store.openAssistant();
};
</script>
