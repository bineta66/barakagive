<template>
  <div class="p-6 space-y-6 bg-white min-h-screen">
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-3xl font-bold text-or">Historique des paiements</h1>
        <p class="text-sm text-gray-500 mt-1">
          Toutes vos transactions PayTech.
        </p>
      </div>
    </div>

    <LoadingSpinner v-if="loading" message="Chargement de l'historique..." />

    <div v-else-if="transactions.length === 0" class="text-center py-12">
      <svg xmlns="http://www.w3.org/2000/svg" class="w-16 h-16 mx-auto text-slate-300 mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5">
        <path stroke-linecap="round" stroke-linejoin="round" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
      </svg>
      <h3 class="text-lg font-semibold text-slate-900 mb-2">Aucun paiement</h3>
      <p class="text-gray-500">Aucune transaction n'a été effectuée pour le moment.</p>
    </div>

    <div v-else class="bg-white border border-slate-200 rounded-xl overflow-hidden shadow-sm">
      <table class="w-full">
        <thead class="bg-slate-50 text-xs font-bold uppercase text-slate-500">
          <tr>
            <th class="text-left px-6 py-4">Date</th>
            <th class="text-left px-6 py-4">Montant</th>
            <th class="text-left px-6 py-4">Statut</th>
            <th class="text-left px-6 py-4">Période</th>
            <th class="text-left px-6 py-4">Référence</th>
            <th class="text-left px-6 py-4">Actions</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-slate-100">
          <tr v-for="tx in transactions" :key="tx.id" class="hover:bg-slate-50/50">
            <td class="px-6 py-4 text-sm text-slate-700">{{ tx.created_at_formatted }}</td>
            <td class="px-6 py-4 text-sm font-semibold text-slate-900">{{ formatPrice(tx.montant) }} FCFA</td>
            <td class="px-6 py-4">
              <span class="px-3 py-1 rounded-full text-xs font-semibold" :class="txStatusClass(tx.statut)">
                {{ txStatusLabel(tx.statut) }}
              </span>
            </td>
            <td class="px-6 py-4 text-sm text-slate-600">
              {{ tx.period_start_formatted }} → {{ tx.period_end_formatted }}
            </td>
            <td class="px-6 py-4 text-sm text-slate-500 font-mono">{{ tx.transaction_id }}</td>
            <td class="px-6 py-4">
              <div class="flex items-center gap-2">
                <button
                  v-if="tx.statut === 'SUCCESS'"
                  @click="downloadReceipt(tx)"
                  class="text-xs text-bleu-nuit hover:underline flex items-center gap-1"
                >
                  <svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                  </svg>
                  Reçu
                </button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>

      <!-- Pagination -->
      <div v-if="totalPages > 1" class="flex items-center justify-between px-6 py-4 border-t">
        <p class="text-sm text-slate-500">
          Page {{ currentPage }} sur {{ totalPages }} ({{ totalCount }} transactions)
        </p>
        <div class="flex gap-2">
          <button
            @click="currentPage--"
            :disabled="currentPage === 1"
            class="px-3 py-1 border rounded text-sm disabled:opacity-50"
          >
            Précédent
          </button>
          <button
            @click="currentPage++"
            :disabled="currentPage === totalPages"
            class="px-3 py-1 border rounded text-sm disabled:opacity-50"
          >
            Suivant
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from "vue"
import { useAuthStore } from "@/stores/auth"
import api from "@/services/api.js"
import LoadingSpinner from "@/components/ui/LoadingSpinner.vue"

const authStore = useAuthStore()

const transactions = ref([])
const loading = ref(true)
const currentPage = ref(1)
const pageSize = ref(10)
const totalCount = ref(0)
const totalPages = computed(() => Math.ceil(totalCount.value / pageSize.value))

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

const formatPrice = (val) => new Intl.NumberFormat("fr-FR").format(val || 0)

const fetchTransactions = async () => {
  loading.value = true
  try {
    const res = await api.get("/api/payment/history/", {
      params: { page: currentPage.value, page_size: pageSize.value }
    })
    transactions.value = res.data.results || res.data
    totalCount.value = res.data.count || transactions.value.length
  } catch (err) {
    console.error("Failed to load transactions", err)
  } finally {
    loading.value = false
  }
}

const downloadReceipt = (tx) => {
  // TODO: Générer et télécharger le reçu PDF
  alert(`Téléchargement du reçu pour ${tx.transaction_id}`)
}

onMounted(() => {
  fetchTransactions()
})
</script>