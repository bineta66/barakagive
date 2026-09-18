<template>
  <div class="min-h-screen bg-white flex items-center justify-center p-6">
    <div class="w-full max-w-md">
      <div class="text-center mb-8">
        <div class="w-24 h-24 mx-auto mb-6 rounded-full bg-red-100 flex items-center justify-center">
          <svg xmlns="http://www.w3.org/2000/svg" class="w-12 h-12 text-red-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5">
            <path stroke-linecap="round" stroke-linejoin="round" d="M12 9v3.75m9-.75a9 9 0 11-18 0 9 9 0 0118 0zm-9 3.75h.008v.008H12v-.008z" />
          </svg>
        </div>
        <h1 class="text-3xl font-bold text-slate-900 mb-2">Essai gratuit terminé</h1>
        <p class="text-gray-500 text-lg">
          Votre période d'essai gratuit de 7 jours est arrivée à expiration.
        </p>
      </div>

      <div class="bg-white border border-slate-200 rounded-xl p-6 shadow-sm mb-6">
        <p class="text-gray-600 mb-4">
          Pour continuer à utiliser BarakaGive360 et accéder à toutes les fonctionnalités, 
          vous devez activer votre abonnement mensuel.
        </p>

        <div class="bg-slate-50 p-4 rounded-lg border border-slate-200 mb-4">
          <div class="flex items-center justify-between mb-2">
            <span class="text-sm text-slate-500">Abonnement mensuel</span>
            <span class="text-2xl font-bold text-or">50 000 FCFA / mois</span>
          </div>
          <p class="text-xs text-slate-500">Renouvellement automatique • Résiliation libre</p>
        </div>

        <AlertMessage v-if="error" type="error" :message="error" :dismissible="true" @dismiss="error = null" />

        <button
          v-if="!loading"
          @click="initiatePayment"
          class="w-full py-4 bg-red-600 text-white text-lg font-bold rounded-lg hover:bg-red-700 transition shadow-lg flex items-center justify-center gap-3"
        >
          <svg xmlns="http://www.w3.org/2000/svg" class="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
            <path stroke-linecap="round" stroke-linejoin="round" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1" />
          </svg>
          Payer 50 000 FCFA avec PayTech
        </button>

        <div v-else class="flex justify-center items-center gap-3 py-4">
          <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-white"></div>
          <span class="text-white">Redirection vers PayTech...</span>
        </div>

        <p class="text-center text-xs text-gray-500 mt-4">
          Vous serez redirigé vers le portail sécurisé PayTech pour finaliser le paiement.
        </p>
      </div>

      <div class="text-center text-sm text-gray-500">
        <p>Besoin d'aide ? <a href="mailto:support@barakagive.com" class="text-or hover:underline">Contactez le support</a></p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from "vue"
import { useAuthStore } from "@/stores/auth"
import api from "@/services/api.js"
import AlertMessage from "@/components/ui/AlertMessage.vue"

const authStore = useAuthStore()

const loading = ref(false)
const error = ref(null)

const initiatePayment = async () => {
  loading.value = true
  error.value = null
  try {
    const res = await api.post("/api/payment/subscribe/")
    window.location.href = res.data.payment_url
  } catch (err) {
    loading.value = false
    error.value = err.response?.data?.detail || "Erreur lors de la création du paiement"
  }
}
</script>