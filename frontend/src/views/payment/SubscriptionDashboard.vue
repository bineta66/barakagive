<template>
  <div class="p-6 space-y-6 bg-white min-h-screen">
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-3xl font-bold text-or">Mon abonnement</h1>
        <p class="text-sm text-gray-500 mt-1">
          Gérer votre abonnement BarakaGive360.
        </p>
      </div>
    </div>

    <!-- Alert si expiré -->
    <div v-if="subscription.statut === 'EXPIRED'" class="p-4 bg-red-50 border border-red-200 rounded-xl text-red-700">
      <h3 class="font-bold mb-1">❌ Votre abonnement a expiré</h3>
      <p class="text-sm">Vous devez renouveler pour accéder aux fonctionnalités.</p>
    </div>

    <!-- Carte principale -->
    <div class="bg-white border border-slate-200/60 rounded-xl p-6 shadow-sm">
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        <div class="bg-white border border-slate-200 rounded-xl p-4">
          <p class="text-xs font-bold uppercase text-slate-500">Plan</p>
          <p class="text-xl font-bold text-bleu-nuit mt-1">{{ subscription.plan }}</p>
        </div>
        <div class="bg-white border border-slate-200 rounded-xl p-4">
          <p class="text-xs font-bold uppercase text-slate-500">Statut</p>
          <p class="text-xl font-bold mt-1">
            <span class="px-3 py-1 rounded-full text-xs font-semibold" :class="statusClass">
              {{ statusLabel }}
            </span>
          </p>
        </div>
        <div class="bg-white border border-slate-200 rounded-xl p-4">
          <p class="text-xs font-bold uppercase text-slate-500">Prix mensuel</p>
          <p class="text-xl font-bold text-or mt-1">{{ formatPrice(subscription.prix) }} FCFA</p>
        </div>
        <div class="bg-white border border-slate-200 rounded-xl p-4">
          <p class="text-xs font-bold uppercase text-slate-500">Prochain paiement</p>
          <p class="text-xl font-bold text-bleu-nuit mt-1">{{ subscription.next_payment_date_formatted || '—' }}</p>
        </div>
      </div>

      <!-- Détails -->
      <div class="space-y-4">
        <div class="bg-slate-50 p-4 rounded-lg border border-slate-200">
          <h3 class="text-sm font-bold text-slate-900 mb-2">Détails de l'abonnement</h3>
          <dl class="grid grid-cols-2 gap-2 text-sm">
            <dt class="text-slate-500">Date de début essai</dt>
            <dd class="font-semibold">{{ subscription.trial_end ? formatDate(subscription.trial_start) : '—' }}</dd>
            <dt class="text-slate-500">Fin d'essai / Expiration</dt>
            <dd class="font-semibold">{{ subscription.trial_end_formatted || subscription.next_payment_date_formatted || '—' }}</dd>
            <dt class="text-slate-500">Jours restants</dt>
            <dd class="font-semibold text-or">{{ subscription.days_remaining }} jour(s)</dd>
            <dt class="text-slate-500">Statut actuel</dt>
            <dd class="font-semibold">
              <span class="px-2 py-0.5 rounded text-xs" :class="statusClass">{{ statusLabel }}</span>
            </dd>
          </dl>
        </div>

        <!-- Actions -->
        <div class="flex flex-wrap gap-3 pt-4 border-t border-slate-200">
          <router-link
            v-if="subscription.statut === 'TRIAL' || subscription.statut === 'EXPIRED'"
            to="/payment/subscribe"
            class="px-6 py-3 bg-bleu-nuit text-white font-semibold rounded-lg hover:bg-[#01111eff] transition shadow-sm flex items-center gap-2"
          >
            <svg xmlns="http://www.w3.org/2000/svg" class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
              <path stroke-linecap="round" stroke-linejoin="round" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            {{ subscription.statut === 'EXPIRED' ? 'Payer avec PayTech' : 'Activer mon abonnement' }}
          </router-link>

          <router-link
            v-if="subscription.statut === 'ACTIVE'"
            to="/payment/history"
            class="px-6 py-3 bg-slate-100 text-slate-700 font-semibold rounded-lg hover:bg-slate-200 transition flex items-center gap-2"
          >
            <svg xmlns="http://www.w3.org/2000/svg" class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
              <path stroke-linecap="round" stroke-linejoin="round" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
            Historique des paiements
          </router-link>

          <button
            v-if="subscription.statut === 'ACTIVE'"
            @click="cancelSubscription"
            class="px-6 py-3 bg-red-50 text-red-700 font-semibold rounded-lg hover:bg-red-100 transition flex items-center gap-2"
          >
            <svg xmlns="http://www.w3.org/2000/svg" class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
              <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12" />
            </svg>
            Annuler l'abonnement
          </button>
        </div>
      </div>
    </div>

    <!-- Historique des paiements -->
    <div class="bg-white border border-slate-200/60 rounded-xl p-6 shadow-sm">
      <h2 class="text-lg font-bold text-slate-900 mb-4">Historique des paiements</h2>

      <div v-if="transactions.length === 0" class="text-center py-8 text-gray-500">
        Aucun paiement effectué pour le moment.
      </div>

      <div v-else class="overflow-x-auto">
        <table class="w-full">
          <thead>
            <tr class="text-left text-xs font-bold uppercase text-slate-500 border-b border-slate-200">
              <th class="pb-3 px-4">Date</th>
              <th class="pb-3 px-4">Montant</th>
              <th class="pb-3 px-4">Statut</th>
              <th class="pb-3 px-4">Référence</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-100">
            <tr v-for="tx in transactions" :key="tx.id" class="hover:bg-slate-50/50">
              <td class="py-3 px-4 text-sm text-slate-700">{{ tx.created_at_formatted }}</td>
              <td class="py-3 px-4 text-sm font-semibold text-slate-900">{{ formatPrice(tx.montant) }} FCFA</td>
              <td class="py-3 px-4">
                <span class="px-2 py-1 rounded text-xs font-semibold" :class="txStatusClass(tx.statut)">
                  {{ txStatusLabel(tx.statut) }}
                </span>
              </td>
              <td class="py-3 px-4 text-sm text-slate-500 font-mono">{{ tx.transaction_id }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from "vue"
import { useAuthStore } from "@/stores/auth"
import api from "@/services/api.js"

const authStore = useAuthStore()

const subscription = ref(null)
const transactions = ref([])
const loading = ref(true)

const statusClass = computed(() => {
  switch (subscription.value?.statut) {
    case "TRIAL": return "bg-amber-100 text-amber-800"
    case "ACTIVE": return "bg-green-100 text-green-800"
    case "EXPIRED": return "bg-red-100 text-red-800"
    case "CANCELLED": return "bg-gray-100 text-gray-800"
    default: return "bg-gray-100 text-gray-800"
  }
})

const statusLabel = computed(() => {
  switch (subscription.value?.statut) {
    case "TRIAL": return "Essai gratuit"
    case "ACTIVE": return "Actif"
    case "EXPIRED": return "Expiré"
    case "CANCELLED": return "Annulé"
    default: return "Inconnu"
  }
})

const txStatusClass = (statut) => {
  switch (statut) {
    case "SUCCESS": return "bg-green-100 text-green-800"
    case "PENDING": return "bg-amber-100 text-amber-800"
    case "FAILED": return "bg-red-100 text-red-800"
    case "CANCELLED": return "bg-gray-100 text-gray-800"
    default: return "bg-gray-100 text-gray-800"
  }
}

const txStatusLabel = (statut) => {
  switch (statut) {
    case "SUCCESS": return "Réussi"
    case "PENDING": return "En attente"
    case "FAILED": return "Échoué"
    case "CANCELLED": return "Annulé"
    default: return statut
  }
}

const formatPrice = (val) => {
  return new Intl.NumberFormat("fr-FR").format(val || 0)
}

const formatDate = (iso) => {
  if (!iso) return "—"
  return new Date(iso).toLocaleDateString("fr-FR", {
    day: "numeric",
    month: "long",
    year: "numeric",
  })
}

const fetchSubscription = async () => {
  loading.value = true
  try {
    const res = await api.get("/api/payment/subscription/detail/")
    subscription.value = res.data
  } catch (err) {
    console.error("Failed to load subscription", err)
  } finally {
    loading.value = false
  }
}

const fetchTransactions = async () => {
  try {
    const res = await api.get("/api/payment/history/")
    transactions.value = res.data
  } catch (err) {
    console.error("Failed to load transactions", err)
  }
}

const cancelSubscription = async () => {
  if (!confirm("Êtes-vous sûr de vouloir annuler votre abonnement ?")) return
  try {
    await api.post("/api/payment/subscription/cancel/")
    await fetchSubscription()
  } catch (err) {
    console.error("Failed to cancel subscription", err)
  }
}

onMounted(async () => {
  await Promise.all([fetchSubscription(), fetchTransactions()])
})
</script>