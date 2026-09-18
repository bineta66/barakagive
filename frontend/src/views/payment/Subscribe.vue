<template>
  <div class="p-6 space-y-6 bg-white min-h-screen max-w-3xl mx-auto">
    <div class="text-center mb-8">
      <div class="w-20 h-20 mx-auto mb-4 rounded-full bg-or/10 flex items-center justify-center">
        <svg xmlns="http://www.w3.org/2000/svg" class="w-10 h-10 text-or" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5">
          <path stroke-linecap="round" stroke-linejoin="round" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1" />
        </svg>
      </div>
      <h1 class="text-3xl font-bold text-or">Activer mon abonnement</h1>
      <p class="text-gray-500 mt-2">
        {{ subscription.statut === 'EXPIRED' 
          ? 'Votre période d\'essai est terminée. Activez votre abonnement pour continuer.' 
          : 'Votre essai gratuit se termine dans ' + subscription.days_remaining + ' jour(s). Activez maintenant pour continuer sans interruption.' }}
      </p>
    </div>

    <!-- Résumé du paiement -->
    <div class="bg-white border border-slate-200 rounded-xl p-6 shadow-sm mb-6">
      <h2 class="text-lg font-bold text-slate-900 mb-4">Résumé du paiement</h2>
      <dl class="grid grid-cols-2 gap-4 text-sm">
        <dt class="text-slate-500">Plan</dt>
        <dd class="font-semibold">{{ subscription.plan }}</dd>
        <dt class="text-slate-500">Prix mensuel</dt>
        <dd class="font-bold text-2xl text-or">{{ formatPrice(subscription.prix) }} FCFA</dd>
        <dt class="text-slate-500">Période</dt>
        <dd class="font-semibold">Mensuel (renouvellement automatique)</dd>
        <dt class="text-slate-500">Mode de paiement</dt>
        <dd class="font-semibold">PayTech Sénégal</dd>
      </dl>
    </div>

    <!-- Informations importantes -->
    <div class="bg-blue-50 border border-blue-200 rounded-xl p-4 mb-6">
      <h3 class="font-bold text-blue-800 mb-2 flex items-center gap-2">
        <svg xmlns="http://www.w3.org/2000/svg" class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
          <path stroke-linecap="round" stroke-linejoin="round" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        Informations importantes
      </h3>
      <ul class="text-sm text-blue-700 space-y-1 list-disc list-inside">
        <li>Paiement sécurisé via <strong>PayTech Sénégal</strong></li>
        <li>Renouvellement automatique chaque mois (50 000 FCFA)</li>
        <li>Résiliation possible à tout moment</li>
        <li>Reçu envoyé par email après chaque paiement</li>
      </ul>
    </div>

    <!-- Erreur -->
    <AlertMessage v-if="error" type="error" :message="error" :dismissible="true" @dismiss="error = null" />

    <!-- Bouton de paiement -->
    <div class="space-y-4">
      <button
        v-if="!loading"
        @click="initiatePayment"
        class="w-full py-4 bg-bleu-nuit text-white text-lg font-bold rounded-lg hover:bg-[#01111eff] transition shadow-lg flex items-center justify-center gap-3"
      >
        <svg xmlns="http://www.w3.org/2000/svg" class="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
          <path stroke-linecap="round" stroke-linejoin="round" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1" />
        </svg>
        Payer 50 000 FCFA avec PayTech
      </button>

      <div v-else class="flex justify-center items-center gap-3 py-4">
        <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-white"></div>
        <span class="text-white">Redirection vers PayTech...</span>
      </div>

      <p class="text-center text-xs text-gray-500">
        Vous serez redirigé vers le portail sécurisé PayTech pour finaliser le paiement.
      </p>
    </div>

    <!-- Retour -->
    <div class="text-center pt-6 border-t border-slate-200">
      <router-link to="/payment" class="text-sm text-slate-500 hover:text-slate-700 underline">
        ← Retour à mon abonnement
      </router-link>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from "vue"
import { useRouter } from "vue-router"
import { useAuthStore } from "@/stores/auth"
import api from "@/services/api.js"
import AlertMessage from "@/components/ui/AlertMessage.vue"

const router = useRouter()
const authStore = useAuthStore()

const subscription = ref(null)
const loading = ref(false)
const error = ref(null)

const formatPrice = (val) => new Intl.NumberFormat("fr-FR").format(val || 0)

const fetchSubscription = async () => {
  if (!authStore.isGerant) return
  try {
    const res = await api.get("/api/payment/subscription/")
    subscription.value = res.data
  } catch (err) {
    console.error("Failed to load subscription", err)
  }
}

const initiatePayment = async () => {
  loading.value = true
  error.value = null
  try {
    const res = await api.post("/api/payment/subscribe/")
    // Rediriger vers l'URL PayTech
    window.location.href = res.data.payment_url
  } catch (err) {
    loading.value = false
    error.value = err.response?.data?.detail || "Erreur lors de la création du paiement"
  }
}

onMounted(() => {
  fetchSubscription()
})
</script>