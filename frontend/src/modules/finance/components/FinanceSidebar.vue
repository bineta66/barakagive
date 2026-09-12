<template>
  <aside class="w-64 min-h-screen bg-slate-900 flex flex-col justify-between">
    <div>
      <div class="px-5 pt-5 pb-4 flex items-center gap-3 border-b border-slate-800">
        <img
          src="@/assets/images/image.png"
          alt="Logo BarakaGive"
          class="w-10 h-10 object-contain"
        />
        <span class="text-lg font-bold text-white">BarakaGive</span>
      </div>

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
          <span class="text-sm">{{ item.nom }}</span>
        </RouterLink>
      </nav>
    </div>

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
import { useRoute } from "vue-router"
import {
  LayoutDashboard,
  FolderKanban,
  Wallet,
  HandHeart,
  Receipt,
  FileText,
  BarChart3,
  LogOut,
} from "lucide-vue-next"

const route = useRoute()

const menus = [
  { nom: "Tableau de bord Finance", route: "/finance/dashboard", icon: LayoutDashboard },
  { nom: "Projets assignés", route: "/finance/projets", icon: FolderKanban },
  { nom: "Budgets", route: "/finance/budgets", icon: Wallet },
  { nom: "Dons & Financements", route: "/finance/dons", icon: HandHeart },
  { nom: "Dépenses", route: "/finance/depenses", icon: Receipt },
  { nom: "Justificatifs", route: "/finance/justificatifs", icon: FileText },
  { nom: "Rapports financiers", route: "/finance/rapports", icon: BarChart3 },
]
</script>
