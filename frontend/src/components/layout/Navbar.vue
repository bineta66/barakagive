<template>
  <div
    class="h-16 w-full bg-transparent px-4 sm:px-6 flex items-center justify-between"
  >
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
          class="glass-control w-full h-10 pl-10 pr-4 text-sm placeholder:text-slate-400"
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
      <div class="relative">
        <button type="button" class="flex items-center gap-2 rounded-xl p-1.5 text-left hover:bg-slate-100 focus:outline-none focus:ring-2 focus:ring-bleu-nuit/30" :aria-expanded="authStore.role === 'SUPER_ADMIN' ? profileMenuOpen : undefined" :aria-haspopup="authStore.role === 'SUPER_ADMIN' ? 'menu' : undefined" aria-label="Menu du profil" @click="authStore.role === 'SUPER_ADMIN' && (profileMenuOpen = !profileMenuOpen)">
          <span class="flex h-10 w-10 items-center justify-center rounded-full bg-bleu-nuit/10"><User :size="18" class="text-bleu-nuit" /></span>
          <span class="hidden text-right sm:block"><span class="block text-sm font-semibold text-slate-900">{{ displayName }}</span><span class="block text-[11px] font-medium uppercase tracking-wide text-slate-500">{{ displayRole }}</span></span>
        </button>
        <div v-if="profileMenuOpen && authStore.role === 'SUPER_ADMIN'" class="absolute right-0 top-12 z-50 w-56 rounded-xl border border-slate-200 bg-white p-2 shadow-lg" role="menu">
          <p class="border-b border-slate-100 px-3 py-2 text-xs text-slate-500">{{ displayRole }}</p>
          <button type="button" class="w-full rounded-lg px-3 py-2 text-left text-sm font-medium text-slate-700 hover:bg-slate-50 focus:outline-none focus:ring-2 focus:ring-bleu-nuit/30" @click="signOut">Se déconnecter</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onBeforeUnmount, ref, watch } from "vue";
import { useRouter } from "vue-router";
import { Bell, Search, User } from "lucide-vue-next";
import { useAuthStore } from "@/stores/auth";
import api from "@/services/api";


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
  profileMenuOpen.value = false;
  await authStore.logout();
  router.push("/connexion");
};
</script>
