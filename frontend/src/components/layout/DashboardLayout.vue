<template>
  <div class="flex min-h-screen bg-white">
    <!-- Sidebar mobile (overlay) -->
    <transition name="fade">
      <div
        v-if="mobileOpen"
        class="fixed inset-0 z-40 bg-slate-900/50 lg:hidden"
        @click="mobileOpen = false"
      ></div>
    </transition>

    <aside
      :class="[
        'fixed top-0 z-50 h-screen bg-bleu-nuit transition-all duration-300 ease-in-out flex flex-col',
        mobileOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0',
        'w-72 lg:w-64',
      ]"
    >
      <Sidebar @close="mobileOpen = false" />
    </aside>

    <div class="flex-1 flex flex-col min-w-0 lg:ml-64">
      <header class="sticky top-0 z-30 h-16 bg-white border-b border-slate-200 shadow-xs-sm flex items-center px-4 gap-3">
        <button
          type="button"
          class="lg:hidden inline-flex items-center justify-center w-10 h-10 rounded-lg text-slate-700 hover:bg-slate-100"
          @click="mobileOpen = !mobileOpen"
          aria-label="Ouvrir le menu"
        >
          <svg xmlns="http://www.w3.org/2000/svg" class="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
            <path stroke-linecap="round" stroke-linejoin="round" d="M4 6h16M4 12h16M4 18h16" />
          </svg>
        </button>
        <Navbar />
      </header>

      <!-- Trial Banner - Gérant only -->
      <TrialBanner v-if="isGerant" />

      <main class="flex-1 p-4 sm:p-6">
        <router-view v-slot="{ Component }">
          <component :is="Component" />
        </router-view>
      </main>
    </div>

    <!-- Executive Orbital IA - Gérant only -->
    <ExecutiveOrbitalIA v-if="isGerant" />

    <!-- Financial Orbital - Responsable Finance only -->
    <FinancialOrbital v-if="isFinance" />
  </div>
</template>

<script setup>
import { ref, computed } from "vue"
import { useAuthStore } from "@/stores/auth"
import Sidebar from "@/components/layout/Sidebar.vue"
import Navbar from "@/components/layout/Navbar.vue"
import ExecutiveOrbitalIA from "@/components/ia/ExecutiveOrbitalIA.vue"
import FinancialOrbital from "@/components/ia/FinancialOrbital.vue"
import TrialBanner from "@/components/payment/TrialBanner.vue"

const mobileOpen = ref(false)
const authStore = useAuthStore()

const isGerant = computed(() => authStore.role === "GERANT")
const isFinance = computed(() => authStore.role === "FINANCE")
</script>

<style scoped>
.fade-enter-active, .fade-leave-active {
  transition: opacity 0.2s ease;
}
.fade-enter-from, .fade-leave-to {
  opacity: 0;
}
</style>