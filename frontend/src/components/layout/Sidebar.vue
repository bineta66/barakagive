<template>
  <aside class="w-64 min-h-screen bg-bleu-nuit flex flex-col justify-between">
    <!-- Haut : Logo + Menu -->
    <div>
      <!-- Logo -->
      <div class="px-5 pt-5 pb-4 flex items-center justify-between border-b border-gray-800">
        <div class="flex items-center gap-3">
          <img
            src="@/assets/images/image.png"
            alt="Logo BarakaGive"
            class="w-10 h-10 object-contain"
          />
          <span class="text-lg font-bold text-white">BarakaGive</span>
        </div>
        <button
          type="button"
          class="lg:hidden inline-flex items-center justify-center w-8 h-8 rounded-md text-gray-400 hover:text-white hover:bg-gray-800 transition"
          @click="$emit('close')"
          aria-label="Fermer le menu"
        >
          <svg xmlns="http://www.w3.org/2000/svg" class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
            <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>

      <!-- Menu -->
      <nav class="mt-3 px-2 space-y-1">
        <RouterLink
          v-for="item in menus"
          :key="item.nom"
          :to="item.route"
          class="flex items-center gap-3 h-12 px-4 rounded-lg transition-all"
          :class="
            route.path === item.route
              ? 'bg-or text-white'
              : 'text-white hover:bg-gray-800'
          "
        >
          <component :is="item.icon" :size="20" />
          <span
            class="text-sm"
            :class="route.path === item.route ? 'font-semibold' : 'font-medium'"
          >
            {{ item.nom }}
          </span>
        </RouterLink>
      </nav>
    </div>

    <!-- Bas : Déconnexion -->
    <div class="px-5 pb-5">
      <div class="border-t border-gray-800 mb-4"></div>

      <button
        type="button"
        @click="seDeconnecter"
        class="w-full flex items-center gap-3 text-white hover:text-red-400 transition"
      >
        <LogOut :size="20" class="text-white" />
        <span class="text-sm font-medium">Se déconnecter</span>
      </button>
    </div>
  </aside>
</template>

<script setup>
import { computed } from "vue";
import { useRoute, useRouter } from "vue-router";
import { LogOut } from "lucide-vue-next";
import { useAuthStore } from "@/stores/auth.js";
import { getMenusForRole } from "@/config/menusConfig.js";

const route = useRoute();
const router = useRouter();
const authStore = useAuthStore();

const routePrefixToRole = {
  "/super-admin": "Super Administrateur",
  "/agent": "Agent de terrain",
  "/gerant": "Gérant",
  "/finance": "Responsable Finance",
  "/chef-projet": "Chef de projet",
};

const currentRouteRole = computed(() => {
  for (const [prefix, roleLabel] of Object.entries(routePrefixToRole)) {
    if (route.path.startsWith(prefix)) {
      return roleLabel;
    }
  }

  // Fallback to user role
  switch (authStore.role) {
    case "SUPER_ADMIN":
      return "Super Administrateur";
    case "GERANT":
      return "Gérant";
    case "CHEF_PROJET":
      return "Chef de projet";
    case "AGENT":
      return "Agent de terrain";
    case "FINANCE":
      return "Responsable Finance";
    default:
      return "Chef de projet";
  }
});

const menus = computed(() => getMenusForRole(currentRouteRole.value));

const seDeconnecter = async () => {
  await authStore.logout();
  router.push("/connexion");
};
</script>

