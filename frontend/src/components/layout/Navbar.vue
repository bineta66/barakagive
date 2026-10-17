<template>
  <div
    class="h-16 w-full bg-transparent px-3 sm:px-6 flex items-center justify-between gap-2 sm:gap-4"
  >
    <!-- Recherche -->
    <div class="flex-1 max-w-md min-w-0">
      <div class="relative">
        <Search
          :size="16"
          class="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400 shrink-0"
        />
        <input
          type="text"
          placeholder="Rechercher..."
          class="glass-control w-full h-9 sm:h-10 pl-8 sm:pl-10 pr-3 sm:pr-4 text-xs sm:text-sm placeholder:text-slate-400 rounded-xl"
        />
      </div>
    </div>

    <!-- Notifications internes et profil -->
    <div class="flex items-center gap-3">
      <div class="relative">
        <button type="button" @click="notificationPanelOpen = !notificationPanelOpen" class="relative flex h-10 w-10 items-center justify-center rounded-xl text-bleu-nuit hover:bg-white/70" aria-label="Notifications">
          <Bell :size="19" />
          <span v-if="unreadCount" class="absolute right-1 top-1 min-w-4 rounded-full bg-[#D20C4F] px-1 text-[10px] font-bold leading-4 text-white">{{ unreadCount > 9 ? '9+' : unreadCount }}</span>
        </button>
        <div v-if="notificationPanelOpen" class="absolute right-0 top-12 z-50 w-[min(22rem,calc(100vw-2rem))] overflow-hidden rounded-2xl border border-slate-200 bg-white text-slate-800">
          <div class="flex items-center justify-between border-b border-slate-100 px-4 py-3">
            <h3 class="text-sm font-semibold text-bleu-nuit">Notifications</h3>
            <button type="button" @click="notificationPanelOpen = false" class="text-xs text-slate-500 hover:text-bleu-nuit">Fermer</button>
          </div>
          <div class="max-h-80 overflow-y-auto">
            <p v-if="notifications.length === 0" class="px-4 py-6 text-center text-xs text-slate-500">Aucune notification.</p>
            <button v-for="item in notifications" :key="item.id" type="button" @click="markNotificationRead(item)" class="block w-full border-b border-slate-100 px-4 py-3 text-left hover:bg-slate-50" :class="item.read ? 'opacity-70' : ''">
              <span class="flex items-start gap-2">
                <span class="mt-1.5 h-2 w-2 shrink-0 rounded-full" :class="item.read ? 'bg-slate-300' : 'bg-[#D20C4F]'" />
                <span class="min-w-0">
                  <span class="block text-xs font-semibold text-bleu-nuit">{{ item.title }}</span>
                  <span class="mt-1 block text-xs leading-relaxed text-slate-600">{{ item.message }}</span>
                  <span class="mt-1 block text-[10px] text-slate-400">{{ item.project ? `${item.project} · ` : '' }}{{ formatNotificationDate(item.created_at) }}</span>
                </span>
              </span>
            </button>
          </div>
        </div>
      </div>
      <!-- Profil Utilisateur (Icône Personne) -->
      <div class="relative">
        <button
          type="button"
          class="flex items-center gap-2 rounded-xl p-1.5 text-left hover:bg-slate-100 focus:outline-none focus:ring-2 focus:ring-bleu-nuit/30 transition"
          aria-haspopup="dialog"
          aria-label="Informations du profil utilisateur"
          @click="openProfileModal"
        >
          <span class="flex h-10 w-10 items-center justify-center rounded-full bg-bleu-nuit/10 text-bleu-nuit">
            <User :size="18" />
          </span>
          <span class="hidden text-right sm:block">
            <span class="block text-sm font-semibold text-slate-900">{{ displayName }}</span>
            <span class="block text-[11px] font-medium uppercase tracking-wide text-slate-500">{{ displayRole }}</span>
          </span>
        </button>
      </div>
    </div>

    <!-- Modal Profil Utilisateur : Affiche STRICTEMENT les informations de la personne et Se déconnecter (AUCUNE fonctionnalité) -->
    <Teleport to="body">
      <transition name="fade">
        <div
          v-if="profileModalOpen"
          class="fixed inset-0 z-[100] bg-black/60 backdrop-blur-sm"
          @click="profileModalOpen = false"
        />
      </transition>

      <transition name="modal-pop">
        <div
          v-if="profileModalOpen"
          class="fixed inset-x-0 bottom-0 sm:bottom-auto sm:top-1/2 sm:left-1/2 sm:-translate-x-1/2 sm:-translate-y-1/2 z-[101] max-w-sm sm:max-w-md w-full bg-white rounded-t-[32px] sm:rounded-3xl shadow-2xl border border-slate-100 p-6 flex flex-col text-slate-800"
          role="dialog"
          aria-modal="true"
          aria-label="Informations de la personne"
        >
          <!-- Poignée tactile iOS mobile -->
          <button
            type="button"
            class="w-12 h-1.5 bg-slate-300 rounded-full mx-auto mb-3 sm:hidden hover:bg-slate-400"
            @click="profileModalOpen = false"
            aria-label="Fermer"
          />

          <!-- En-tête -->
          <div class="flex items-center justify-between pb-3 border-b border-slate-100">
            <div>
              <h3 class="text-base font-bold text-bleu-nuit">Profil utilisateur</h3>
              <p class="text-xs text-slate-500">Informations du compte connecté</p>
            </div>
            <button
              type="button"
              @click="profileModalOpen = false"
              class="w-8 h-8 rounded-full bg-slate-100 hover:bg-slate-200 flex items-center justify-center text-slate-500 hover:text-slate-800 transition"
              aria-label="Fermer"
            >
              <X :size="16" />
            </button>
          </div>

          <!-- Informations de la personne (AUCUNE fonctionnalité) -->
          <div class="py-5 space-y-4">
            <div class="flex items-center gap-4">
              <div class="w-14 h-14 rounded-2xl bg-bleu-nuit text-white flex items-center justify-center font-bold text-lg shadow-md ring-4 ring-bleu-nuit/10 shrink-0">
                {{ userInitials }}
              </div>
              <div class="min-w-0 flex-1">
                <h4 class="text-base font-bold text-bleu-nuit truncate leading-tight">
                  {{ displayName }}
                </h4>
                <p class="text-xs text-slate-500 truncate mt-0.5">
                  {{ userEmail }}
                </p>
                <div class="mt-2 flex flex-wrap items-center gap-1.5">
                  <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-[11px] font-semibold bg-bleu-nuit/10 text-bleu-nuit border border-bleu-nuit/20">
                    {{ displayRole }}
                  </span>
                  <span class="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[11px] font-semibold bg-bleu-accent/10 text-bleu-accent border border-bleu-accent/20">
                    <span class="w-1.5 h-1.5 rounded-full bg-bleu-accent" />
                    Compte actif
                  </span>
                </div>
              </div>
            </div>

            <!-- Fiche récapitulative -->
            <div class="rounded-2xl bg-slate-50/80 border border-slate-200/60 p-3.5 space-y-2 text-xs">
              <div class="flex items-center justify-between">
                <span class="text-slate-500">Organisation :</span>
                <span class="font-semibold text-bleu-nuit truncate max-w-[200px]">{{ userOrg }}</span>
              </div>
              <div class="flex items-center justify-between">
                <span class="text-slate-500">Courriel :</span>
                <span class="font-mono text-[11px] text-slate-700 truncate max-w-[200px]">{{ userEmail }}</span>
              </div>
              <div class="flex items-center justify-between">
                <span class="text-slate-500">Rôle :</span>
                <span class="font-semibold text-bleu-nuit">{{ displayRole }}</span>
              </div>
            </div>
          </div>

          <!-- Bouton UNIQUE : Se déconnecter -->
          <div class="hidden pt-2 border-t border-slate-100 md:block">
            <button
              type="button"
              @click="signOut"
              class="w-full flex items-center justify-center gap-2 py-3 px-4 rounded-xl bg-rose-baraka/10 hover:bg-rose-baraka text-rose-baraka hover:text-white border border-rose-baraka/30 text-sm font-bold transition-all duration-200 active:scale-[0.98]"
            >
              <LogOut :size="18" />
              Se déconnecter
            </button>
          </div>
        </div>
      </transition>
    </Teleport>
  </div>
</template>

<script setup>
import { computed, onBeforeUnmount, ref, watch } from "vue";
import { useRouter } from "vue-router";
import { Bell, Search, User, X, LogOut } from "lucide-vue-next";
import { useAuthStore } from "@/stores/auth";
import api from "@/services/api";

const profileModalOpen = ref(false);

const openProfileModal = () => {
  profileModalOpen.value = true;
};


const authStore = useAuthStore();
const router = useRouter();
const notifications = ref([]);
const unreadCount = ref(0);
const notificationPanelOpen = ref(false);
const profileMenuOpen = ref(false);
let notificationPollTimer = null;

const stopNotificationPolling = () => {
  if (notificationPollTimer !== null) {
    window.clearInterval(notificationPollTimer);
    notificationPollTimer = null;
  }
};

const loadNotifications = async () => {
  try {
    const { data } = await api.get("/api/accounts/notifications/");
    notifications.value = data.results || [];
    unreadCount.value = data.unread_count || 0;
  } catch {
    // The navbar remains usable if notifications are temporarily unavailable.
  }
};

const markNotificationRead = async (item) => {
  if (item.read) return;
  try {
    await api.post(`/api/accounts/notifications/${item.id}/read/`);
    item.read = true;
    unreadCount.value = Math.max(0, unreadCount.value - 1);
  } catch {
    // Keep the unread state if the server did not confirm the update.
  }
};

const formatNotificationDate = (value) => {
  if (!value) return "";
  return new Date(value).toLocaleString("fr-FR", { dateStyle: "short", timeStyle: "short" });
};

const stopWatchingAuth = watch(() => authStore.accessToken, (token) => {
  stopNotificationPolling();
  if (!token) {
    notifications.value = [];
    unreadCount.value = 0;
    return;
  }
  loadNotifications();
  notificationPollTimer = window.setInterval(loadNotifications, 60000);
}, { immediate: true });
onBeforeUnmount(() => {
  stopNotificationPolling();
  stopWatchingAuth();
});

const displayName = computed(
  () => authStore.nom || authStore.user?.email || "Utilisateur"
);

const userEmail = computed(
  () => authStore.email || authStore.user?.email || "Courriel non renseigné"
);

const userOrg = computed(
  () => authStore.user?.organization_name || authStore.user?.organization || "BarakaGive Platform"
);

const userInitials = computed(() => {
  const name = displayName.value || "";
  const parts = name.trim().split(" ");
  if (parts.length >= 2 && parts[0] && parts[1]) {
    return (parts[0][0] + parts[1][0]).toUpperCase();
  }
  return (name.slice(0, 2) || "BG").toUpperCase();
});

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

const signOut = async () => {
  profileModalOpen.value = false;
  profileMenuOpen.value = false;
  await authStore.logout();
  router.push("/connexion");
};
</script>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.25s ease;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

.modal-pop-enter-active {
  transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
}
.modal-pop-leave-active {
  transition: all 0.2s ease-in;
}
.modal-pop-enter-from {
  opacity: 0;
  transform: translateY(24px) scale(0.96);
}
.modal-pop-leave-to {
  opacity: 0;
  transform: translateY(16px) scale(0.97);
}
</style>
