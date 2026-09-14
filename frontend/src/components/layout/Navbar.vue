<template>
  <header class="h-16 bg-white  flex items-center justify-between px-6">
    <!-- Recherche -->
    <div class="relative w-96">
      <Search
        :size="18"
        class="absolute left-3 top-1/2 -translate-y-1/2 text-zinc-500"
      />

      <input
        type="text"
        placeholder="Rechercher projet, zone, ONG..."
        class="w-full h-10 pl-10 pr-4 rounded-lg border border-slate-200 bg-white text-sm placeholder:text-zinc-500 focus:outline-none focus:ring-2 focus:ring-or"
      />
    </div>

    <!-- Profil -->
    <div class="flex items-center gap-6">
      <!-- Notification -->
      <button class="relative text-zinc-700 hover:text-or transition">
        <Bell :size="22" />

        <span
          class="absolute -top-1 -right-1 w-2.5 h-2.5 bg-red-600 rounded-full"
        ></span>
      </button>

      <!-- SÃ©parateur -->
      <div class="w-px h-8 bg-neutral-300"></div>

      <!-- Utilisateur -->
      <div class="flex items-center gap-3">
        <div
          class="w-10 h-10 rounded-full bg-or/10 flex items-center justify-center"
        >
          <User :size="20" class="text-or" />
        </div>

        <div class="text-right">
          <p class="text-sm font-semibold text-slate-900">
            {{ utilisateur.nom }}
          </p>

          <p class="text-[11px] uppercase tracking-wide font-bold text-zinc-600">
            {{ utilisateur.role }}
          </p>
        </div>
      </div>
    </div>
  </header>
</template>

<script setup>
import { Search, Bell, User } from "lucide-vue-next";
import { storeToRefs } from "pinia";
import { useAuthStore } from "@/stores/auth.js";

const authStore = useAuthStore();
const { utilisateur } = storeToRefs(authStore);
</script>

