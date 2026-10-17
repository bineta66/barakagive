<template>
  <button
    type="button"
    @click="store.toggleAssistant"
    title="Assistant IA Exécutif"
    aria-label="Ouvrir l'Assistant IA Exécutif"
    class="fixed bottom-24 lg:bottom-6 right-4 sm:right-6 z-40 group focus:outline-none"
  >
    <!-- Cercle principal glassmorphism -->
    <div
      class="relative w-16 h-16 rounded-full flex items-center justify-center
             bg-[#021427]/90 backdrop-blur-md border-2 border-[#CCA43B]/50
             shadow-[0_8px_32px_rgba(2,20,39,0.6),inset_0_0_20px_rgba(204,164,59,0.08)]
             transition-all duration-300 ease-out
             group-hover:scale-110 group-hover:border-[#CCA43B]/80
             group-hover:shadow-[0_12px_40px_rgba(2,20,39,0.7),0_0_20px_rgba(204,164,59,0.25)]"
      :class="hasAlerts ? 'animate-pulse' : ''"
    >
      <!-- Halo extérieur respirant -->
      <span
        class="absolute inset-0 rounded-full border border-[#CCA43B]/20 animate-ping opacity-60 pointer-events-none"
        style="animation-duration: 2.5s;"
      />

      <!-- Reflet ocre supérieur -->
      <span
        class="absolute top-0 left-1/2 -translate-x-1/2 w-8 h-3 rounded-full
               bg-gradient-to-b from-[#CCA43B]/20 to-transparent blur-sm pointer-events-none"
      />

      <!-- Icône cerveau + étincelle -->
      <span class="relative z-10 flex items-center justify-center">
        <!-- Brain SVG -->
        <svg
          xmlns="http://www.w3.org/2000/svg"
          width="26" height="26"
          viewBox="0 0 24 24" fill="none"
          stroke="#CCA43B" stroke-width="1.6"
          stroke-linecap="round" stroke-linejoin="round"
          class="transition-transform duration-300 group-hover:scale-110"
        >
          <path d="M12 5a3 3 0 1 0-5.997.125 4 4 0 0 0-2.526 5.77
                   4 4 0 0 0 .556 6.588A4 4 0 1 0 12 18Z"/>
          <path d="M12 5a3 3 0 1 1 5.997.125 4 4 0 0 1 2.526 5.77
                   4 4 0 0 1-.556 6.588A4 4 0 1 1 12 18Z"/>
          <path d="M15 13a4.5 4.5 0 0 1-3-4 4.5 4.5 0 0 1-3 4"/>
          <path d="M17.599 6.5a3 3 0 0 0 .399-1.375"/>
          <path d="M6.003 5.125A3 3 0 0 0 6.401 6.5"/>
          <path d="M3.477 10.896a4 4 0 0 1 .585-.396"/>
          <path d="M19.938 10.5a4 4 0 0 1 .585.396"/>
          <path d="M6 18a4 4 0 0 1-1.967-.516"/>
          <path d="M19.967 17.484A4 4 0 0 1 18 18"/>
        </svg>

        <!-- Étincelle dorée en superposition -->
        <svg
          xmlns="http://www.w3.org/2000/svg"
          width="13" height="13"
          viewBox="0 0 24 24" fill="none"
          stroke="#FFD700" stroke-width="2.2"
          stroke-linecap="round" stroke-linejoin="round"
          class="absolute -top-2 -right-2 animate-spin"
          style="animation-duration: 6s;"
        >
          <path d="M9.937 15.5A2 2 0 0 0 8.5 14.063l-6.135-1.582a.5.5 0 0 1 0-.962
                   L8.5 9.936A2 2 0 0 0 9.937 8.5l1.582-6.135a.5.5 0 0 1 .963 0
                   L14.063 8.5A2 2 0 0 0 15.5 9.937l6.135 1.581a.5.5 0 0 1 0 .964
                   L15.5 14.063a2 2 0 0 0-1.437 1.437l-1.582 6.135a.5.5 0 0 1-.963 0z"/>
        </svg>
      </span>

      <!-- Badge alerte rouge -->
      <span
        v-if="hasAlerts"
        class="absolute -top-1 -right-1 flex h-5 w-5 items-center justify-center
               rounded-full bg-red-600 text-[9px] font-bold text-white
               shadow-md border-2 border-[#021427] z-20"
      >!</span>
    </div>
  </button>
</template>

<script setup>
import { computed } from "vue"
import { useAssistantStore } from "@/stores/assistant.js"

const store = useAssistantStore()

// Affiche le badge rouge si la dernière réponse contient une erreur
const hasAlerts = computed(() =>
  store.lastMessage?.isError === true
)
</script>
