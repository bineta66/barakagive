<template>
  <div
    v-if="showBanner && !isDismissed"
    class="relative w-full py-3 px-4 bg-gradient-to-r from-orange-50 to-amber-50 border-b border-amber-200"
    role="alert"
  >
    <div
      class="max-w-7xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-4"
    >
      <!-- Icône + Texte -->
      <div class="flex items-center gap-3">
        <div
          class="flex-shrink-0 w-8 h-8 rounded-full bg-amber-100 flex items-center justify-center"
        >
          <svg
            xmlns="http://www.w3.org/2000/svg"
            class="w-5 h-5 text-amber-600"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
            stroke-width="2"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
            />
          </svg>
        </div>
        <div class="text-sm text-amber-800">
          <template v-if="subscription.statut === 'TRIAL'">
            <strong
              >Essai gratuit : {{ subscription.days_remaining }} jour{{
                subscription.days_remaining > 1 ? "s" : ""
              }}
              restant{{ subscription.days_remaining > 1 ? "s" : "" }}</strong
            >
            <br />
            <span class="text-xs">
              Votre période d'essai se termine le
              <strong>{{ formatDate(subscription.trial_end) }}</strong
              >.
            </span>
          </template>
          <template
            v-else-if="
              subscription.statut === 'ACTIVE' &&
              subscription.days_remaining <= 3
            "
          >
            <strong
              >⚠️ Votre abonnement expire dans
              {{ subscription.days_remaining }} jour{{
                subscription.days_remaining > 1 ? "s" : ""
              }}.</strong
            >
          </template>
          <template v-else-if="subscription.statut === 'EXPIRED'">
            <strong>❌ Votre période d'essai est terminée.</strong>
            <br />
            <span class="text-xs"
              >Activez votre abonnement pour continuer.</span
            >
          </template>
        </div>
      </div>

      <!-- Bouton d'action -->
      <div class="flex flex-shrink-0 items-center gap-2">
        <button
          @click="payerMaintenant"
          :disabled="paying"
          class="inline-flex items-center px-4 py-2 bg-bleu-nuit text-white text-sm font-semibold rounded-lg hover:bg-[#01111eff] transition shadow-sm disabled:opacity-60"
        >
          <span
            v-if="paying"
            class="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin mr-2"
          ></span>
          {{ paying ? "Redirection..." : actionButtonText }}
        </button>
        <button
          type="button"
          @click="hideBanner"
          aria-label="Masquer la bannière d’abonnement"
          title="Masquer cette bannière"
          class="inline-flex h-9 w-9 items-center justify-center rounded-lg text-amber-800 transition hover:bg-amber-100 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-amber-600"
        >
          <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
            <path stroke-linecap="round" stroke-linejoin="round" d="M6 18 18 6M6 6l12 12" />
          </svg>
        </button>
      </div>
    </div>
  </div>
  <button
    v-else-if="showBanner && isDismissed"
    type="button"
    @click="restoreBanner"
    class="fixed right-4 top-[4.75rem] z-40 inline-flex items-center gap-2 rounded-lg border border-amber-200 bg-amber-50 px-3 py-2 text-xs font-semibold text-amber-900 shadow-md transition hover:bg-amber-100 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-amber-600"
  >
    <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
      <path stroke-linecap="round" stroke-linejoin="round" d="M3 12a9 9 0 1 0 2.64-6.36L3 8m0-5v5h5" />
    </svg>
    Afficher la bannière d’essai
  </button>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch } from "vue";
import { useAuthStore } from "@/stores/auth";
import api from "@/services/api.js";

const authStore = useAuthStore();

const subscription = ref(null);
const paying = ref(false);
const isDismissed = ref(false);
let refreshTimer;

const dismissalKey = computed(() => {
  const identity = authStore.user?.id || authStore.user?.email || authStore.organizationId || "gerant";
  return `barakagive:trial-banner-hidden:${identity}`;
});

watch(dismissalKey, (key) => {
  isDismissed.value = typeof window !== "undefined" && window.localStorage.getItem(key) === "true";
}, { immediate: true });

const hideBanner = () => {
  isDismissed.value = true;
  window.localStorage.setItem(dismissalKey.value, "true");
};

const restoreBanner = () => {
  isDismissed.value = false;
  window.localStorage.removeItem(dismissalKey.value);
};

const showBanner = computed(() => {
  if (!subscription.value) return false;
  if (!authStore.isGerant) return false;
  const stat = subscription.value.statut;
  const days = subscription.value.days_remaining;
  return (
    stat === "TRIAL" || (stat === "ACTIVE" && days <= 3) || stat === "EXPIRED"
  );
});

const actionButtonText = computed(() => {
  const stat = subscription.value?.statut;
  if (stat === "EXPIRED") return "Renouveler avec PayTech";
  if (stat === "TRIAL") return "Activer mon abonnement";
  return "Renouveler maintenant";
});

const formatDate = (iso) => {
  if (!iso) return "";
  return new Date(iso).toLocaleDateString("fr-FR", {
    day: "numeric",
    month: "long",
    year: "numeric",
  });
};

const payerMaintenant = async () => {
  paying.value = true;
  try {
    const res = await api.post("/api/payment/subscribe/");
    const url = res.data.payment_url || res.data.redirect_url;
    if (url) {
      window.location.href = url;
    } else {
      paying.value = false;
      alert("Erreur : URL de paiement introuvable");
    }
  } catch (err) {
    paying.value = false;
    const msg =
      err.response?.data?.detail || "Erreur lors de la création du paiement";
    alert(msg);
  }
};

const fetchSubscription = async () => {
  if (!authStore.isGerant) return;
  try {
    const res = await api.get("/api/payment/subscription/");
    subscription.value = res.data;
  } catch (err) {
    console.error("Failed to load subscription for banner", err);
  }
};

onMounted(() => {
  fetchSubscription();
  refreshTimer = setInterval(fetchSubscription, 5 * 60 * 1000);
});

onUnmounted(() => {
  clearInterval(refreshTimer);
});
</script>
