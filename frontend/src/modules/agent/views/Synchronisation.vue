<template>
  <div class="space-y-6 max-w-6xl mx-auto p-4 sm:p-6">
    <!-- Header -->
    <div class="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
      <div>
        <h1 class="text-2xl font-bold text-slate-900">Synchronisation hors-ligne</h1>
        <p class="text-sm text-slate-500 mt-1">
          Gérer les bénéficiaires collectés sur le terrain en attente de synchronisation avec le serveur
        </p>
      </div>

      <button
        @click="synchroniserTout"
        :disabled="syncing || pendingList.length === 0"
        class="px-5 py-2.5 bg-bleu-nuit text-white font-semibold rounded-xl hover:bg-[#01111eff] transition flex items-center gap-2 shadow-xs disabled:opacity-50"
      >
        <RefreshCw :size="18" :class="syncing ? 'animate-spin' : ''" />
        <span>{{ syncing ? 'Synchronisation en cours...' : 'Synchroniser tout maintenant' }}</span>
      </button>
    </div>

    <!-- Alertes de synchronisation -->
    <AlertMessage v-if="feedback.message" :type="feedback.type" :message="feedback.message" class="mb-4" />

    <!-- Cartes Statuts -->
    <div class="grid grid-cols-1 sm:grid-cols-3 gap-4">
      <div class="bg-white border border-slate-200 rounded-xl p-5 shadow-xs-sm flex items-center justify-between">
        <div>
          <p class="text-xs font-bold uppercase text-slate-500">En attente (IndexedDB)</p>
          <h3 class="text-2xl font-bold text-amber-600 mt-1">{{ pendingList.length }}</h3>
        </div>
        <div class="p-3 bg-amber-50 text-amber-600 rounded-xl">
          <Clock :size="24" />
        </div>
      </div>

      <div class="bg-white border border-slate-200 rounded-xl p-5 shadow-xs-sm flex items-center justify-between">
        <div>
          <p class="text-xs font-bold uppercase text-slate-500">Synchronisés</p>
          <h3 class="text-2xl font-bold text-emerald-600 mt-1">{{ syncedCount }}</h3>
        </div>
        <div class="p-3 bg-emerald-50 text-emerald-600 rounded-xl">
          <CheckCircle :size="24" />
        </div>
      </div>

      <div class="bg-white border border-slate-200 rounded-xl p-5 shadow-xs-sm flex items-center justify-between">
        <div>
          <p class="text-xs font-bold uppercase text-slate-500">Conflits / Doublons</p>
          <h3 class="text-2xl font-bold text-red-600 mt-1">{{ conflictCount }}</h3>
        </div>
        <div class="p-3 bg-red-50 text-red-600 rounded-xl">
          <AlertTriangle :size="24" />
        </div>
      </div>
    </div>

    <!-- Tableau des éléments hors ligne -->
    <div class="bg-white border border-slate-200/60 rounded-xl overflow-hidden shadow-xs-sm">
      <div class="p-5 border-b border-slate-100 flex justify-between items-center">
        <div>
          <h2 class="text-base font-bold text-slate-900">Données stockées localement</h2>
          <p class="text-xs text-slate-500 mt-0.5">Ces enregistrements sont conservés dans votre base de données locale sécurisée</p>
        </div>

        <button
          v-if="syncedCount > 0"
          @click="nettoyerSynchronises"
          class="text-xs font-semibold text-slate-500 hover:text-red-600 transition"
        >
          Purger les synchronisés
        </button>
      </div>

      <div class="overflow-x-auto">
        <table class="w-full">
          <thead class="bg-slate-50 border-b border-slate-200 text-xs font-semibold text-bleu-nuit uppercase tracking-wider">
            <tr>
              <th class="text-left px-5 py-3">Date</th>
              <th class="text-left px-5 py-3">Bénéficiaire</th>
              <th class="text-left px-5 py-3">Téléphone</th>
              <th class="text-left px-5 py-3">Statut de sync</th>
              <th class="text-right px-5 py-3">Action</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-100 text-sm">
            <tr v-for="item in allOfflineItems" :key="item.local_id" class="hover:bg-slate-50 transition">
              <td class="px-5 py-3.5 text-xs text-slate-500 font-mono">
                {{ formatTimestamp(item.timestamp) }}
              </td>
              <td class="px-5 py-3.5 font-semibold text-slate-800">
                {{ item.beneficiary?.prenom }} {{ item.beneficiary?.nom }}
              </td>
              <td class="px-5 py-3.5 text-slate-600">
                {{ item.beneficiary?.telephone || '-' }}
              </td>
              <td class="px-5 py-3.5">
                <span
                  class="inline-block px-2.5 py-1 text-xs font-semibold rounded-full"
                  :class="
                    item.sync_status === 'SYNCED'
                      ? 'bg-emerald-50 text-emerald-700'
                      : item.sync_status === 'CONFLICT'
                      ? 'bg-red-50 text-red-700'
                      : 'bg-amber-50 text-amber-700'
                  "
                >
                  {{ item.sync_status === 'SYNCED' ? 'Synchronisé' : item.sync_status === 'CONFLICT' ? 'Doublon / Conflit' : 'En attente' }}
                </span>
              </td>
              <td class="px-5 py-3.5 text-right">
                <button
                  @click="supprimerLocal(item.local_id)"
                  class="text-xs text-slate-400 hover:text-red-600 font-medium"
                >
                  Supprimer
                </button>
              </td>
            </tr>

            <tr v-if="allOfflineItems.length === 0">
              <td colspan="5" class="p-8 text-center text-sm text-slate-500">
                Aucune donnée stockée hors-ligne pour le moment. Tous vos enregistrements sont à jour.
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, reactive, onMounted } from "vue"
import { RefreshCw, Clock, CheckCircle, AlertTriangle } from "lucide-vue-next"
import AlertMessage from "@/components/ui/AlertMessage.vue"
import { offlineStorage } from "@/services/offlineStorage.js"
import { useBeneficiaryStore } from "@/stores/beneficiary.js"

const beneficiaryStore = useBeneficiaryStore()

const allOfflineItems = ref([])
const syncing = ref(false)
const feedback = reactive({ type: "success", message: "" })

const pendingList = computed(() => {
  return allOfflineItems.value.filter((i) => i.sync_status === "PENDING")
})

const syncedCount = computed(() => {
  return allOfflineItems.value.filter((i) => i.sync_status === "SYNCED").length
})

const conflictCount = computed(() => {
  return allOfflineItems.value.filter((i) => i.sync_status === "CONFLICT").length
})

const chargerDonnees = async () => {
  allOfflineItems.value = await offlineStorage.getAllBeneficiaries()
  await beneficiaryStore.refreshOfflineCounts()
}

onMounted(() => {
  chargerDonnees()
})

const formatTimestamp = (ts) => {
  if (!ts) return "-"
  const d = new Date(ts)
  return d.toLocaleDateString("fr-FR") + " " + d.toLocaleTimeString("fr-FR", { hour: "2-digit", minute: "2-digit" })
}

const synchroniserTout = async () => {
  syncing.value = true
  feedback.message = ""

  try {
    const report = await beneficiaryStore.syncOfflineBeneficiaries()
    await chargerDonnees()

    if (report.total === 0) {
      feedback.type = "info"
      feedback.message = "Aucun enregistrement en attente de synchronisation."
    } else {
      feedback.type = report.failed > 0 ? "warning" : "success"
      feedback.message = `Rapport de synchronisation : ${report.synced} enregistré(s), ${report.conflicts} doublon(s) / conflit(s) détecté(s), ${report.failed} erreur(s).`
    }
  } catch (err) {
    feedback.type = "error"
    feedback.message = "Erreur lors de la synchronisation avec le serveur. Vérifiez votre connexion."
  } finally {
    syncing.value = false
  }
}

const supprimerLocal = async (localId) => {
  if (!confirm("Voulez-vous supprimer cet enregistrement local ?")) return
  await offlineStorage.deleteBeneficiary(localId)
  await chargerDonnees()
}

const nettoyerSynchronises = async () => {
  const syncedItems = allOfflineItems.value.filter((i) => i.sync_status === "SYNCED")
  for (const item of syncedItems) {
    await offlineStorage.deleteBeneficiary(item.local_id)
  }
  await chargerDonnees()
}
</script>

