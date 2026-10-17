<template>
  <div class="lg:hidden">
    <!-- ═══════════════════════════════════════════════════════════════════ -->
    <!-- BARRE FLOTTANTE STYLE IPHONE (DOCK iOS MODERNE)                      -->
    <!-- ═══════════════════════════════════════════════════════════════════ -->
    <nav
      class="fixed bottom-2.5 inset-x-3 sm:inset-x-8 z-40 pointer-events-none flex justify-center pb-[env(safe-area-inset-bottom,0px)]"
      aria-label="Navigation mobile principale"
    >
      <div
        class="pointer-events-auto w-full max-w-md bg-[#00313C]/90 backdrop-blur-2xl border border-white/[0.18] rounded-[26px] p-1.5 shadow-[0_12px_40px_rgba(0,18,24,0.45),0_1px_0_rgba(255,255,255,0.12)_inset] flex items-center justify-around gap-1 relative select-none"
      >
        <!-- Onglets principaux -->
        <RouterLink
          v-for="item in primaryTabs"
          :key="item.route"
          :to="item.route"
          :class="[
            'relative flex flex-col items-center justify-center flex-1 min-w-0 py-1.5 px-1 rounded-2xl transition-all duration-200 active:scale-90',
            isRouteActive(item.route)
              ? 'bg-white/[0.16] shadow-sm ring-1 ring-white/20 text-white'
              : 'text-white/60 hover:text-white/90 hover:bg-white/[0.06]'
          ]"
        >
          <!-- Badge de notification / demande / sync -->
          <span
            v-if="item.route === '/super-admin/demandes' && pendingRequestsCount"
            class="absolute top-1 right-2 flex h-4 min-w-4 items-center justify-center rounded-full bg-[#D20C4F] px-1 text-[9px] font-bold text-white shadow-sm ring-2 ring-[#00313C] animate-pulse"
          >
            {{ pendingRequestsCount > 99 ? '99+' : pendingRequestsCount }}
          </span>

          <span
            v-else-if="item.route === '/agent/synchronisation' && syncPendingCount"
            class="absolute top-1 right-2 flex h-4 min-w-4 items-center justify-center rounded-full bg-amber-500 px-1 text-[9px] font-bold text-white shadow-sm ring-2 ring-[#00313C] animate-pulse"
          >
            {{ syncPendingCount > 99 ? '99+' : syncPendingCount }}
          </span>

          <!-- Icône -->
          <component
            :is="item.icon"
            :size="20"
            :class="[
              'transition-transform duration-200 shrink-0',
              isRouteActive(item.route) ? 'scale-110 text-white' : 'text-white/70'
            ]"
            :stroke-width="isRouteActive(item.route) ? 2.4 : 1.9"
          />

          <!-- Nom de l'onglet -->
          <span
            class="text-[10px] font-medium tracking-tight truncate max-w-full mt-0.5"
            :class="isRouteActive(item.route) ? 'font-semibold text-white' : 'text-white/70'"
          >
            {{ item.shortNom || item.nom }}
          </span>

          <!-- Puce lumineuse active (indicateur iOS) -->
          <span
            v-if="isRouteActive(item.route)"
            class="w-1 h-1 rounded-full bg-[#D20C4F] shadow-[0_0_8px_#D20C4F] mt-0.5 shrink-0"
          />
        </RouterLink>

        <!-- 5e Onglet : Bouton "Plus" / Menu iOS si plus de 4 items -->
        <button
          v-if="hasOverflow"
          type="button"
          @click="sheetOpen = !sheetOpen"
          :class="[
            'relative flex flex-col items-center justify-center flex-1 min-w-0 py-1.5 px-1 rounded-2xl transition-all duration-200 active:scale-90',
            sheetOpen || isOverflowActive
              ? 'bg-white/[0.16] shadow-sm ring-1 ring-white/20 text-white'
              : 'text-white/60 hover:text-white/90 hover:bg-white/[0.06]'
          ]"
          :aria-expanded="sheetOpen"
          aria-label="Ouvrir le menu complet"
        >
          <!-- Badge si un élément secondaire a une alerte -->
          <span
            v-if="overflowHasAlerts"
            class="absolute top-1 right-2 flex h-2 w-2 rounded-full bg-[#D20C4F] ring-2 ring-[#00313C] animate-pulse"
          />

          <!-- Icône Grille / Plus -->
          <LayoutGrid
            :size="20"
            :class="[
              'transition-transform duration-200 shrink-0',
              sheetOpen || isOverflowActive ? 'scale-110 text-white' : 'text-white/70'
            ]"
            :stroke-width="sheetOpen || isOverflowActive ? 2.4 : 1.9"
          />

          <!-- Label dynamique (si une page secondaire est active, affiche son nom, sinon "Plus") -->
          <span
            class="text-[10px] font-medium tracking-tight truncate max-w-full mt-0.5"
            :class="sheetOpen || isOverflowActive ? 'font-semibold text-white' : 'text-white/70'"
          >
            {{ activeOverflowItem ? (activeOverflowItem.shortNom || activeOverflowItem.nom) : 'Plus' }}
          </span>

          <!-- Puce lumineuse active -->
          <span
            v-if="isOverflowActive || sheetOpen"
            class="w-1 h-1 rounded-full bg-[#D20C4F] shadow-[0_0_8px_#D20C4F] mt-0.5 shrink-0"
          />
        </button>
      </div>
    </nav>

    <!-- ═══════════════════════════════════════════════════════════════════ -->
    <!-- FEUILLE MODALE iOS (BOTTOM SHEET ACTION DRAWER)                    -->
    <!-- ═══════════════════════════════════════════════════════════════════ -->
    <!-- Arrière-plan flouté avec transition -->
    <transition name="fade">
      <div
        v-if="sheetOpen"
        class="fixed inset-0 z-50 bg-black/60 backdrop-blur-sm"
        @click="sheetOpen = false"
      />
    </transition>

    <!-- Tiroir coulissant du bas style iOS -->
    <transition name="slide-up">
      <div
        v-if="sheetOpen"
        class="fixed bottom-0 inset-x-0 z-50 max-h-[88vh] overflow-y-auto bg-[#00313C]/95 backdrop-blur-3xl border-t border-white/20 rounded-t-[32px] text-white p-5 pb-10 shadow-[0_-12px_45px_rgba(0,0,0,0.55)] flex flex-col"
        role="dialog"
        aria-modal="true"
        aria-label="Menu complet de navigation"
      >
        <!-- Poignée iOS (Drag handle) -->
        <button
          type="button"
          class="w-12 h-1.5 bg-white/30 rounded-full mx-auto mb-4 hover:bg-white/50 active:scale-95 transition"
          @click="sheetOpen = false"
          aria-label="Fermer le menu"
        />

        <!-- En-tête : Profil Utilisateur -->
        <div class="flex items-center justify-between pb-4 border-b border-white/[0.12]">
          <div class="flex items-center gap-3 min-w-0">
            <div
              class="w-11 h-11 rounded-2xl bg-gradient-to-tr from-rose-baraka/80 to-bleu-accent flex items-center justify-center font-bold text-base text-white shadow-inner ring-2 ring-white/20 shrink-0"
            >
              {{ userInitials }}
            </div>
            <div class="min-w-0">
              <h3 class="text-sm font-bold text-white truncate leading-tight">
                {{ userName }}
              </h3>
              <p class="text-[11px] font-medium text-white/70 truncate mt-0.5">
                {{ userRoleLabel }}
              </p>
            </div>
          </div>

          <!-- Bouton de fermeture discret -->
          <button
            type="button"
            @click="sheetOpen = false"
            class="w-8 h-8 rounded-full bg-white/10 hover:bg-white/20 flex items-center justify-center text-white/80 hover:text-white transition active:scale-90"
            aria-label="Fermer"
          >
            <X :size="16" />
          </button>
        </div>

        <!-- Section 1 : Pages complémentaires / Toutes les rubriques -->
        <div class="mt-4">
          <p class="text-[11px] font-semibold uppercase tracking-wider text-white/50 mb-3 px-1">
            Toutes les fonctionnalités
          </p>

          <div class="grid grid-cols-1 sm:grid-cols-2 gap-2">
            <RouterLink
              v-for="item in allMenus"
              :key="item.route"
              :to="item.route"
              @click="sheetOpen = false"
              :class="[
                'flex items-center gap-3 p-3 rounded-2xl transition-all duration-200 border',
                isRouteActive(item.route)
                  ? 'bg-white/20 border-white/30 shadow-sm'
                  : 'bg-white/[0.07] border-white/10 hover:bg-white/[0.12] active:scale-[0.98]'
              ]"
            >
              <div
                :class="[
                  'w-10 h-10 rounded-xl flex items-center justify-center shrink-0 transition-colors',
                  isRouteActive(item.route)
                    ? 'bg-white text-bleu-nuit font-bold shadow-md'
                    : 'bg-white/10 text-white'
                ]"
              >
                <component :is="item.icon" :size="20" />
              </div>

              <div class="min-w-0 flex-1">
                <div class="flex items-center justify-between gap-1">
                  <span
                    class="text-xs font-semibold truncate"
                    :class="isRouteActive(item.route) ? 'text-white' : 'text-white/90'"
                  >
                    {{ item.nom }}
                  </span>
                  <span
                    v-if="isRouteActive(item.route)"
                    class="inline-flex items-center gap-1 rounded-full bg-bleu-accent/30 px-1.5 py-0.5 text-[9px] font-bold text-white ring-1 ring-bleu-accent/50"
                  >
                    <Check :size="10" /> Actif
                  </span>
                </div>
                <p class="text-[11px] text-white/60 truncate mt-0.5">
                  {{ item.description || 'Accéder au module' }}
                </p>
              </div>

              <ChevronRight :size="16" class="text-white/40 shrink-0" />
            </RouterLink>
          </div>
        </div>

        <!-- Section 2 : Action de déconnexion rapide -->
        <div class="mt-5 hidden pt-4 border-t border-white/[0.12] md:block">
          <button
            type="button"
            @click="handleLogout"
            class="w-full flex items-center justify-center gap-2 py-3 px-4 rounded-xl bg-rose-baraka/20 hover:bg-rose-baraka/35 text-xs font-semibold text-white border border-rose-baraka/40 transition active:scale-95"
          >
            <LogOut :size="16" /> Se déconnecter
          </button>
        </div>

        <!-- Indicateur d'accueil iOS (Home Indicator Bar) -->
        <div class="w-32 h-1 bg-white/20 rounded-full mx-auto mt-6 shrink-0" />
      </div>
    </transition>
  </div>
</template>

<script setup>
import { ref, computed, inject, watch } from "vue";
import { useRoute, useRouter } from "vue-router";
import { storeToRefs } from "pinia";
import {
  LayoutGrid,
  X,
  ChevronRight,
  LogOut,
  Check,
} from "lucide-vue-next";
import { useAuthStore } from "@/stores/auth.js";
import { getMenusForRole } from "@/config/menusConfig.js";
import { useSuperAdminStore } from "@/modules/super-admin/stores/superAdminStore.js";

const emit = defineEmits(["open-sidebar"]);

const route = useRoute();
const router = useRouter();
const authStore = useAuthStore();
const superAdminStore = useSuperAdminStore();
const { dashboard } = storeToRefs(superAdminStore);

const sheetOpen = ref(false);

// Injection des statistiques de synchronisation offline (si disponibles via App.vue)
const syncStats = inject("syncStats", ref({ pending: 0 }));

// Mapping des routes vers le libellé de rôle
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

// Tous les menus configurés pour ce rôle
const allMenus = computed(() => getMenusForRole(currentRouteRole.value));

// Séparation des onglets : jusqu'à 4 ou 5 max selon le nombre d'items
const primaryTabs = computed(() => {
  if (allMenus.value.length <= 5) {
    return allMenus.value;
  }
  // Pour les rôles à > 5 items (Chef de projet, Gérant, Finance) :
  // On prend les 4 premiers items marqués mobilePrimary (ou les 4 premiers par défaut)
  const primaries = allMenus.value.filter((m) => m.mobilePrimary);
  return primaries.length >= 4 ? primaries.slice(0, 4) : allMenus.value.slice(0, 4);
});

// Items secondaires affichés dans la feuille modale
const secondaryMenus = computed(() => {
  if (allMenus.value.length <= 5) {
    return [];
  }
  const primaryRoutes = new Set(primaryTabs.value.map((m) => m.route));
  return allMenus.value.filter((m) => !primaryRoutes.has(m.route));
});

const hasOverflow = computed(() => secondaryMenus.value.length > 0);

// Vérifie si une route cible est active
const isRouteActive = (targetRoute) => {
  if (!targetRoute) return false;
  if (route.path === targetRoute) return true;
  if (targetRoute.endsWith("/dashboard")) {
    return route.path === targetRoute;
  }
  return route.path.startsWith(targetRoute);
};

// Vérifie si une route de la section "Plus" est active
const isOverflowActive = computed(() => {
  return secondaryMenus.value.some((item) => isRouteActive(item.route));
});

// Item secondaire actif pour adapter dynamiquement le libellé du bouton "Plus"
const activeOverflowItem = computed(() => {
  return secondaryMenus.value.find((item) => isRouteActive(item.route));
});

// Compteurs et badges
const pendingRequestsCount = computed(() => dashboard.value?.ongs?.pending || 0);
const syncPendingCount = computed(() => syncStats.value?.pending || 0);
const overflowHasAlerts = computed(() => {
  return secondaryMenus.value.some(
    (item) => item.route === "/super-admin/demandes" && pendingRequestsCount.value > 0
  );
});

// Infos utilisateur
const userName = computed(() => authStore.nom || authStore.user?.email || "Utilisateur");
const userRoleLabel = computed(() => currentRouteRole.value);
const userInitials = computed(() => {
  const name = userName.value.trim();
  if (!name) return "BG";
  const parts = name.split(" ");
  if (parts.length >= 2) {
    return (parts[0][0] + parts[1][0]).toUpperCase();
  }
  return name.slice(0, 2).toUpperCase();
});

// Chargement automatique du dashboard SuperAdmin si nécessaire pour les badges
watch(
  currentRouteRole,
  (role) => {
    if (role === "Super Administrateur" && !dashboard.value) {
      superAdminStore.fetchDashboard().catch(() => {});
    }
  },
  { immediate: true }
);

// Déconnexion
const handleLogout = async () => {
  sheetOpen.value = false;
  await authStore.logout();
  router.push("/connexion");
};

// Méthodes de contrôle de la feuille modale exposées
const toggleSheet = () => {
  sheetOpen.value = !sheetOpen.value;
};
const openSheet = () => {
  sheetOpen.value = true;
};
const closeSheet = () => {
  sheetOpen.value = false;
};

defineExpose({
  toggleSheet,
  openSheet,
  closeSheet,
  sheetOpen,
});
</script>

<style scoped>
/* Animations fluides style iOS */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.25s ease;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

.slide-up-enter-active {
  transition: transform 0.32s cubic-bezier(0.16, 1, 0.3, 1), opacity 0.25s ease;
}
.slide-up-leave-active {
  transition: transform 0.24s cubic-bezier(0.4, 0, 0.7, 0.2), opacity 0.2s ease;
}
.slide-up-enter-from,
.slide-up-leave-to {
  transform: translateY(100%);
  opacity: 0;
}
</style>
