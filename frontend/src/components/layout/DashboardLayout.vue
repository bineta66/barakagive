<template>
  <div class="flex min-h-screen bg-slate-50">
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
        'fixed top-0 z-50 h-screen bg-bleu-nuit/90 backdrop-blur-2xl border-r border-white/[0.12] transition-all duration-300 ease-in-out flex flex-col',
        mobileOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0',
        'w-72 lg:w-64',
      ]"
    >
      <Sidebar @close="mobileOpen = false" />
    </aside>

    <div class="flex-1 flex flex-col min-w-0 lg:ml-64">
      <header
        class="sticky top-0 z-30 h-16 bg-white/75 backdrop-blur-xl border-b border-white/70 flex items-center px-4 gap-3 transition-all duration-300"
      >
        <button
          type="button"
          class="lg:hidden inline-flex items-center justify-center w-10 h-10 rounded-lg text-slate-700 hover:bg-slate-100"
          @click="mobileOpen = !mobileOpen"
          aria-label="Ouvrir le menu"
        >
          <svg
            xmlns="http://www.w3.org/2000/svg"
            class="w-6 h-6"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
            stroke-width="2"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              d="M4 6h16M4 12h16M4 18h16"
            />
          </svg>
        </button>
        <Navbar />
      </header>

      <!-- Trial Banner - Gérant only -->
      <TrialBanner v-if="isGerant" />

      <main class="glass-theme flex-1 bg-slate-50 p-4 sm:p-6">
        <router-view v-slot="{ Component }">
          <component :is="Component" />
        </router-view>
      </main>
    </div>

    <!-- Executive Assistant IA - Gérant only -->
    <ExecutiveAssistant v-if="isGerant" />

    <!-- Assistant IA Finance - Responsable Finance only -->
    <template v-if="isFinance">
      <FinanceAssistantOrb />
      <FinanceAssistantDrawer />
    </template>
  </div>
</template>

<script setup>
import { ref, computed } from "vue";
import { useRoute } from "vue-router";
import { useAuthStore } from "@/stores/auth";
import Sidebar from "@/components/layout/Sidebar.vue";
import Navbar from "@/components/layout/Navbar.vue";
import ExecutiveAssistant from "@/components/ia/ExecutiveAssistant.vue";
import TrialBanner from "@/components/payment/TrialBanner.vue";
import FinanceAssistantOrb from "@/modules/finance/components/ia/FinanceAssistantOrb.vue";
import FinanceAssistantDrawer from "@/modules/finance/components/ia/FinanceAssistantDrawer.vue";

const route = useRoute();
const mobileOpen = ref(false);
const authStore = useAuthStore();

const isGerant = computed(() => authStore.role === "GERANT");
const isFinance = computed(() => authStore.role === "FINANCE" || route.path.startsWith("/finance"));
</script>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
