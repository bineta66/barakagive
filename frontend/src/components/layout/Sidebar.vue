<template>
  <aside class="w-64 min-h-screen bg-slate-900 flex flex-col justify-between">

    <!-- Haut : Logo + Menu -->
    <div>
      <!-- Logo -->
      <div class="px-5 pt-5 pb-4 flex items-center gap-3 border-b border-slate-800">
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
              ? 'bg-amber-800 text-white'
              : 'text-slate-200 hover:bg-slate-800 hover:text-white'
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
      <div class="border-t border-slate-700 mb-4"></div>

      <button
        class="w-full flex items-center gap-3 text-slate-200 hover:text-red-400 transition"
      >
        <LogOut :size="20" />
        <span class="text-sm font-medium">Se déconnecter</span>
      </button>
    </div>
  </aside>
</template>

<script setup>
import { useRoute } from "vue-router";
import {
  LayoutDashboard,
  FolderKanban,
  ClipboardList,
  Users,
  MapPinned,
  Wallet,
  Handshake,
  Landmark,
  BarChart3,
  LogOut,
} from "lucide-vue-next";

const route = useRoute();

const menus = [
  {
    nom: "Tableau de bord",
    route: "/chef-projet/dashboard",
    icon: LayoutDashboard,
  },
  {
    nom: "Projets",
    route: "/chef-projet/projets",
    icon: FolderKanban,
  },
  {
    nom: "Campagnes",
    route: "/chef-projet/campagnes",
    icon: ClipboardList,
  },
  {
    nom: "Bénéficiaires",
    route: "/chef-projet/beneficiaires",
    icon: Users,
  },
  {
    nom: "Zones",
    route: "/chef-projet/zones",
    icon: MapPinned,
  },
  {
    nom: "Finances",
    route: "/chef-projet/finances",
    icon: Wallet,
  },
  {
    nom: "Partenaires",
    route: "/chef-projet/partenaires",
    icon: Handshake,
  },
  {
    nom: "Bailleurs",
    route: "/chef-projet/bailleurs",
    icon: Landmark,
  },
  {
    nom: "Rapports d’impact",
    route: "/chef-projet/rapports",
    icon: BarChart3,
  },
];
</script>