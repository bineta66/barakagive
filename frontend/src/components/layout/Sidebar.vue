<template>
  <aside class="w-64 min-h-screen bg-bleu-nuit flex flex-col justify-between">
    <!-- Haut : Logo + Menu -->
    <div>
      <!-- Logo -->
      <div class="px-5 pt-5 pb-4 flex items-center gap-3 border-b border-gray-800">
        <img
          src="@/assets/images/image.png"
          alt="Logo BarakaGive"
          class="w-10 h-10 object-contain"
        />
        <span class="text-lg font-bold text-white">BarakaGive</span>
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

    <!-- Bas : Info utilisateur + DÃ©connexion -->
    <div class="px-5 pb-5">
      <div class="border-t border-bleu-nuit/30 mb-4"></div>

      <button
        @click="seDeconnecter"
        class="w-full flex items-center gap-3 text-white hover:text-red-400 transition"
      >
        <LogOut :size="20" class="text-white" />
        <span class="text-sm font-medium">Se dÃ©connecter</span>
      </button>
    </div>
  </aside>
</template>

<script setup>
import { useRoute } from "vue-router";
import { User, LogOut } from "lucide-vue-next";
import { storeToRefs } from "pinia";
import { useAuthStore } from "@/stores/auth.js";
import { getMenusForRole } from "@/config/menusConfig.js";
import { computed } from "vue";

const route = useRoute();
const authStore = useAuthStore();
const { utilisateur } = storeToRefs(authStore);

const routePrefixToRole = {
  "/super-admin": "Super Administrateur",
  "/agent": "Agent de terrain",
  "/gerant": "GÃ©rant",
  "/finance": "Responsable Finance",
  "/chef-projet": "Chef de projet",
};

const currentRouteRole = computed(() => {
  for (const [prefix, role] of Object.entries(routePrefixToRole)) {
    if (route.path.startsWith(prefix)) {
      return role;
    }
  }
  return authStore.role.value;
});

const menus = computed(() => getMenusForRole(currentRouteRole.value));

const seDeconnecter = () => {
  console.log("DÃ©connexion...");
};
</script>

