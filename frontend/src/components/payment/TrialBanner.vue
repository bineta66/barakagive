<template>
  <div
    v-if="showBanner"
    class="relative w-full py-3 px-4 bg-gradient-to-r from-orange-50 to-amber-50 border-b border-amber-200"
    role="alert"
  >
    <div class="max-w-7xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-4">
      <!-- Icône + Texte -->
      <div class="flex items-center gap-3">
        <div class="flex-shrink-0 w-8 h-8 rounded-full bg-amber-100 flex items-center justify-center">
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
            <strong>Essai gratuit : {{ subscription.days_remaining }} jour{{ subscription.days_remaining > 1 ? 's' : '' }} restant{{ subscription.days_remaining > 1 ? 's' : '' }}</strong>
            <br />
            <span class="text-xs">
              Votre période d'essai se termine le <strong>{{ formatDate(subscription.trial_end) }}</strong>.
            </span>
          </template>
          <template v-else-if="subscription.statut === 'ACTIVE' && subscription.days_remaining <= 3">
            <strong>⚠️ Votre abonnement expire dans {{ subscription.days_remaining }} jour{{ subscription.days_remaining > 1 ? 's' : '' }}.</strong>
          </template>
          <template v-else-if="subscription.statut === 'EXPIRED'">
            <strong>❌ Votre période d'essai est terminée.</strong>
            <br />
            <span class="text-xs">Activez votre abonnement pour continuer.</span>
          </template>
        </div>
      </div>

      <!-- Bouton d'action -->
      <div class="flex-shrink-0">
        <router-link
          :to="actionRoute"
          class="inline-flex items-center px-4 py-2 bg-bleu-nuit text-white text-sm font-semibold rounded-lg hover:bg-[#01111eff] transition shadow-sm"
        >
          {{ actionButtonText }}
        </router-link>
      </div>

      
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from "vue"
import { useRouter, useRoute } from "vue-router"
import { useAuthStore } from "@/stores/auth"
import api from "@/services/api.js"

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

const subscription = ref(null)
const dismissed = ref(false)

const showBanner = computed(() => {
  if (!subscription.value || dismissed.value) return false
  if (!authStore.isGerant) return false
  
  // Afficher pour TRIAL (toujours), ACTIVE J-3, EXPIRED
  const stat = subscription.value.statut
  const days = subscription.value.days_remaining
  
  return stat === "TRIAL" || 
         (stat === "ACTIVE" && days <= 3) || 
         stat === "EXPIRED"
})

const actionRoute = computed(() => {
  if (subscription.value.statut === "EXPIRED") return "/payment/expired"
  if (subscription.value.statut === "TRIAL") return "/payment/subscribe"
  return "/payment"
})

const actionButtonText = computed(() => {
  const stat = subscription.value?.statut
  if (stat === "EXPIRED") return "Payer avec PayTech"
  if (stat === "TRIAL") return "Activer mon abonnement"
  return "Renouveler maintenant"
})

const formatDate = (iso) => {
  if (!iso) return ""
  return new Date(iso).toLocaleDateString("fr-FR", {
    day: "numeric",
    month: "long",
    year: "numeric",
  })
}

const fetchSubscription = async () => {
  if (!authStore.isGerant) return
  
  try {
    const res = await api.get("/api/payment/subscription/")
    subscription.value = res.data
  } catch (err) {
    console.error("Failed to load subscription for banner", err)
  }
}

const dismiss = () => {
  dismissed.value = true
  // Re-afficher au prochain rechargement
  setTimeout(() => { dismissed.value = false }, 30000)
}

onMounted(() => {
  fetchSubscription()
  // Rafraîchir toutes les 5 minutes
  setInterval(fetchSubscription, 5 * 60 * 1000)
})
</script>