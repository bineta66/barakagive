<template>
  <div class="h-16 w-full bg-white border-b border-slate-200 px-4 sm:px-6 flex items-center justify-between">

    <!-- Recherche -->
    <div class="flex-1 max-w-md">
      <div class="relative">
        <Search
          :size="18"
          class="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400"
        />
        <input
          type="text"
          placeholder="Rechercher projet, zone, ONG..."
          class="w-full h-10 pl-10 pr-4 rounded-lg border border-slate-200 bg-white text-sm placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-orange-500 "
        />
      </div>
    </div>

    <!-- Profil à droite -->
    <div class="flex items-center gap-3 ml-8 shrink-0">
      <div class="w-10 h-10 rounded-full bg-orange-100 flex items-center justify-center">
        <User :size="18" class="text-orange-600" />
      </div>

      <div class="hidden sm:block text-right">
        <p class="text-sm font-semibold text-slate-900">
          {{ displayName }}
        </p>
        <p class="text-[11px] uppercase tracking-wide font-medium text-slate-500">
          {{ displayRole }}
        </p>
      </div>
    </div>

  </div>
</template>

<script setup>
import { computed } from "vue";
import { Search, User } from "lucide-vue-next";
import { useAuthStore } from "@/stores/auth";

const authStore = useAuthStore();

const displayName = computed(() =>
  authStore.nom || authStore.user?.email || "Utilisateur"
);

  const displayRole = computed(() => {
    switch (authStore.role) {
      case "SUPER_ADMIN":
        return "Super Administrateur";
      case "GERANT":
        return "Gérant";
      case "CHEF_PROJET":
        return "Chef de projet";
      case "FINANCE":
        return "Responsable Finance";
      case "AGENT":
        return "Agent de terrain";
      default:
        return authStore.role || "";
    }
  });
</script>