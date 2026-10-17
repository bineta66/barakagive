<template>
  <div class="flex min-h-screen bg-slate-50">
    <!-- Sidebar desktop uniquement (aucun menu latéral sur mobile) -->
    <aside
      class="hidden lg:flex fixed top-0 z-50 h-screen w-64 bg-bleu-nuit/90 backdrop-blur-2xl border-r border-white/[0.12] flex-col"
    >
      <Sidebar />
    </aside>

    <div class="flex-1 flex flex-col min-w-0 lg:ml-64">
      <header
        class="sticky top-0 z-30 h-16 bg-white/75 backdrop-blur-xl border-b border-white/70 flex items-center px-4 sm:px-6 transition-all duration-300"
      >
        <Navbar />
      </header>

      <!-- Trial Banner - Gérant only -->
      <TrialBanner v-if="isGerant" />

      <!-- Contenu principal avec marge basse de sécurité sur mobile pour le menu iPhone -->
      <main class="glass-theme flex-1 bg-slate-50 p-4 sm:p-6 pb-28 lg:pb-6">
        <router-view v-slot="{ Component }">
          <component :is="Component" />
        </router-view>
      </main>

      <!-- Menu moderne iPhone flottant en bas pour l'ensemble des dashboards et pages -->
      <IPhoneBottomBar ref="iphoneBarRef" />
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
import { ref, computed, provide } from "vue";
import { useRoute } from "vue-router";
import { useAuthStore } from "@/stores/auth";
import Sidebar from "@/components/layout/Sidebar.vue";
import Navbar from "@/components/layout/Navbar.vue";
import IPhoneBottomBar from "@/components/layout/IPhoneBottomBar.vue";
import ExecutiveAssistant from "@/components/ia/ExecutiveAssistant.vue";
import TrialBanner from "@/components/payment/TrialBanner.vue";
import FinanceAssistantOrb from "@/modules/finance/components/ia/FinanceAssistantOrb.vue";
import FinanceAssistantDrawer from "@/modules/finance/components/ia/FinanceAssistantDrawer.vue";

const route = useRoute();
const authStore = useAuthStore();
const iphoneBarRef = ref(null);

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
