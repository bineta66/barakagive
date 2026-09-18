<template>
  <div class="space-y-6 max-w-6xl mx-auto p-4 sm:p-6">
    <!-- Header avec Salutation Personnalisée -->
    <div class="bg-gradient-to-r from-bleu-nuit to-[#0a2540] text-white rounded-2xl p-6 sm:p-8 shadow-xs-md flex flex-col md:flex-row justify-between items-start md:items-center gap-6">
      <div>
        <span class="inline-block px-3 py-1 bg-white/10 text-white/90 text-xs font-semibold rounded-full mb-2">
          Espace Agent de terrain
        </span>
        <h1 class="text-3xl sm:text-4xl font-bold tracking-tight">
          Bonjour, {{ authStore.user?.full_name || authStore.user?.first_name || "Agent" }}
        </h1>
        <p class="text-slate-300 text-sm mt-1">
          Prêt pour la collecte terrain de votre organisation.
        </p>
      </div>

      <!-- Gros bouton Enregistrer un bénéficiaire -->
      <router-link
        to="/agent/collecte"
        class="inline-flex items-center gap-3 px-6 py-4 bg-or text-white text-base font-bold rounded-xl shadow-xs-sm hover:bg-[#633f02] transition-all transform hover:-translate-y-0.5"
      >
        <UserPlus :size="24" />
        <span>Enregistrer un bénéficiaire</span>
      </router-link>
    </div>

    <!-- Alertes & Chargement -->
    <LoadingSpinner v-if="loading" message="Chargement de vos campagnes..." />
    <AlertMessage v-if="error" type="error" :message="error" class="mb-4" />

    <!-- Statut Synchronisation Hors-ligne -->
    <div
      v-if="pendingOfflineCount > 0"
      class="bg-amber-50 border border-amber-200 rounded-xl p-4 flex flex-col sm:flex-row justify-between items-start sm:items-center gap-3"
    >
      <div class="flex items-center gap-3">
        <Clock class="text-amber-600" :size="22" />
        <div>
          <p class="text-sm font-semibold text-amber-900">
            {{ pendingOfflineCount }} enregistrement(s) en attente de synchronisation
          </p>
          <p class="text-xs text-amber-700">
            Ces données sont stockées en toute sécurité sur votre appareil en attendant une connexion réseau.
          </p>
        </div>
      </div>
      <router-link
        to="/agent/sync"
        class="px-4 py-2 bg-amber-600 text-white text-xs font-bold rounded-lg hover:bg-amber-700 transition"
      >
        Synchroniser maintenant
      </router-link>
    </div>

    <!-- Indicateurs Simples -->
    <div class="grid grid-cols-1 sm:grid-cols-3 gap-4">
      <div class="bg-white border border-slate-200 rounded-xl p-5 shadow-xs-sm flex items-center justify-between">
        <div>
          <p class="text-xs font-bold uppercase text-slate-500">Mes campagnes actives</p>
          <h3 class="text-2xl font-bold text-bleu-nuit mt-1">{{ activeCampaignsCount }}</h3>
        </div>
        <div class="p-3 bg-blue-50 text-bleu-nuit rounded-xl">
          <Activity :size="24" />
        </div>
      </div>

      <div class="bg-white border border-slate-200 rounded-xl p-5 shadow-xs-sm flex items-center justify-between">
        <div>
          <p class="text-xs font-bold uppercase text-slate-500">Total campagnes</p>
          <h3 class="text-2xl font-bold text-slate-800 mt-1">{{ campaignStore.campaigns.length }}</h3>
        </div>
        <div class="p-3 bg-slate-50 text-slate-700 rounded-xl">
          <FolderKanban :size="24" />
        </div>
      </div>

      <div class="bg-white border border-slate-200 rounded-xl p-5 shadow-xs-sm flex items-center justify-between">
        <div>
          <p class="text-xs font-bold uppercase text-slate-500">Mode de connexion</p>
          <h3 class="text-lg font-bold mt-1 flex items-center gap-2" :class="isOnline ? 'text-emerald-600' : 'text-orange-600'">
            <span class="w-2.5 h-2.5 rounded-full" :class="isOnline ? 'bg-emerald-500' : 'bg-orange-500'"></span>
            {{ isOnline ? 'En ligne' : 'Hors ligne' }}
          </h3>
        </div>
        <div class="p-3 rounded-xl" :class="isOnline ? 'bg-emerald-50 text-emerald-600' : 'bg-orange-50 text-orange-600'">
          <Wifi v-if="isOnline" :size="24" />
          <WifiOff v-else :size="24" />
        </div>
      </div>
    </div>

    <!-- Mes Campagnes Actives (Tableau) -->
    <div class="bg-white border border-slate-200 rounded-xl shadow-xs-sm overflow-hidden">
      <div class="p-5 border-b border-slate-100 flex justify-between items-center">
        <div>
          <h2 class="text-lg font-bold text-slate-900">Mes campagnes actives</h2>
          <p class="text-xs text-slate-500 mt-0.5">Campagnes actuellement ouvertes pour la collecte de bénéficiaires</p>
        </div>
        <router-link to="/agent/campagnes" class="text-xs font-semibold text-bleu-nuit hover:underline">
          Voir toutes
        </router-link>
      </div>

      <div class="overflow-x-auto">
        <table class="w-full">
          <thead class="bg-slate-50 text-xs font-semibold text-slate-600 uppercase">
            <tr>
              <th class="text-left px-5 py-3">Campagne</th>
              <th class="text-left px-5 py-3">Projet</th>
              <th class="text-left px-5 py-3">Période</th>
              <th class="text-right px-5 py-3">Action</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-100 text-sm">
            <tr v-for="c in activeCampaigns" :key="c.id" class="hover:bg-slate-50 transition">
              <td class="px-5 py-4">
                <span class="font-semibold text-slate-800">{{ c.nom }}</span>
                <p class="text-xs text-slate-400 font-mono">{{ c.code_campagne }}</p>
              </td>
              <td class="px-5 py-4 text-slate-600">{{ c.projet?.name || "-" }}</td>
              <td class="px-5 py-4 text-slate-600 text-xs">
                {{ c.date_debut || "-" }} au {{ c.date_fin || "-" }}
              </td>
              <td class="px-5 py-4 text-right">
                <router-link
                  :to="`/agent/collecte?campagne=${c.id}`"
                  class="inline-flex items-center gap-1.5 px-3 py-1.5 bg-bleu-nuit text-white text-xs font-semibold rounded-lg hover:bg-[#01111eff] transition"
                >
                  <UserPlus :size="14" />
                  Collecter
                </router-link>
              </td>
            </tr>

            <tr v-if="activeCampaigns.length === 0">
              <td colspan="4" class="p-8 text-center text-sm text-slate-500">
                Aucune campagne active actuellement.
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from "vue"
import {
  UserPlus,
  FolderKanban,
  Activity,
  Clock,
  Wifi,
  WifiOff,
} from "lucide-vue-next"
import LoadingSpinner from "@/components/ui/LoadingSpinner.vue"
import AlertMessage from "@/components/ui/AlertMessage.vue"
import { useAuthStore } from "@/stores/auth.js"
import { useCampaignStore } from "@/stores/campaign.js"
import { useBeneficiaryStore } from "@/stores/beneficiary.js"

const authStore = useAuthStore()
const campaignStore = useCampaignStore()
const beneficiaryStore = useBeneficiaryStore()

const loading = ref(false)
const error = ref(null)
const isOnline = ref(typeof navigator !== "undefined" ? navigator.onLine : true)

if (typeof window !== "undefined") {
  window.addEventListener("online", () => (isOnline.value = true))
  window.addEventListener("offline", () => (isOnline.value = false))
}

const activeCampaigns = computed(() => {
  return campaignStore.activeCampaigns.length ? campaignStore.activeCampaigns : campaignStore.campaigns
})

const activeCampaignsCount = computed(() => {
  return activeCampaigns.value.length
})

const pendingOfflineCount = computed(() => {
  return beneficiaryStore.offlineCounts.pending || 0
})

onMounted(async () => {
  loading.value = true
  error.value = null
  try {
    await Promise.allSettled([
      campaignStore.fetchCampaigns(),
      beneficiaryStore.refreshOfflineCounts(),
    ])
  } catch (err) {
    error.value = "Impossible de charger les données de l'agent."
  } finally {
    loading.value = false
  }
})
</script>

