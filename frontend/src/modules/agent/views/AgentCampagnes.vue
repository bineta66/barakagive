<template>
  <div class="mx-auto max-w-7xl space-y-6 px-4 py-5 md:px-6">
    <div class="flex flex-col gap-2 sm:flex-row sm:items-end sm:justify-between">
      <div>
        <p class="text-xs font-bold uppercase tracking-[0.18em] text-amber-700">Espace Agent Terrain</p>
        <h1 class="mt-1 text-2xl font-bold text-slate-900">Mes campagnes</h1>
        <p class="mt-1 text-sm text-slate-500">Campagnes qui vous sont assignées par le chef de projet.</p>
      </div>
      <div class="flex items-center gap-2">
        <span class="inline-flex items-center gap-1.5 rounded-full bg-amber-50 px-3 py-1.5 text-xs font-semibold text-amber-700">
          <span class="w-2 h-2 rounded-full bg-amber-500"></span>
          {{ filteredCampaigns.length }} campagne(s)
        </span>
      </div>
    </div>

    <input v-model="search" type="search" placeholder="Rechercher une campagne..." class="h-11 w-full rounded-xl border border-slate-200 px-4 text-sm outline-none focus:border-amber-700 focus:ring-2 focus:ring-amber-100 sm:w-64" />

    <AlertMessage v-if="error" type="error" :message="error" />
    <LoadingSpinner v-if="loading" message="Chargement des campagnes..." />

    <div v-if="!loading" class="grid grid-cols-1 gap-5 md:grid-cols-2 xl:grid-cols-3">
      <article v-for="campaign in filteredCampaigns" :key="campaign.id" class="overflow-hidden rounded-2xl border border-gray-200 bg-white">
        <div class="relative h-48 bg-gradient-to-br from-slate-900 via-slate-700 to-amber-800">
          <img v-if="campaign.image" :src="campaign.image" :alt="campaign.nom" class="h-full w-full object-cover" />
          <div v-else class="flex h-full items-center justify-center text-5xl font-black text-white/20">BG</div>
          <span class="absolute right-3 top-3 rounded-full px-3 py-1 text-xs font-bold" :class="statusClass(campaign.statut)">{{ statusLabel(campaign.statut) }}</span>
        </div>
        <div class="space-y-4 p-5">
          <div>
            <p class="text-xs font-semibold uppercase tracking-wide text-slate-400">{{ campaign.projet || "Projet humanitaire" }}</p>
            <h2 class="mt-1 text-lg font-bold text-slate-900">{{ campaign.nom }}</h2>
          </div>
          <div class="grid grid-cols-2 gap-3 text-sm">
            <div class="rounded-xl bg-slate-50 p-3">
              <p class="text-xs text-slate-500">Zone assignée</p>
              <p class="mt-1 font-semibold text-slate-800">{{ campaign.zone || "—" }}</p>
            </div>
            <div class="rounded-xl bg-slate-50 p-3">
              <p class="text-xs text-slate-500">Collecte / Objectif</p>
              <p class="mt-1 font-semibold text-slate-800">{{ campaign.collectes || 0 }} / {{ campaign.objectif || 0 }}</p>
            </div>
          </div>
          <div class="flex items-center justify-between text-xs text-slate-500">
            <span>Fin : {{ formatDate(campaign.date_fin) }}</span>
            <span class="font-mono text-slate-400">{{ campaign.code_campagne || "#" + campaign.id.slice(0, 6) }}</span>
          </div>
          <div class="space-y-2">
            <RouterLink :to="`/agent/campagnes/${campaign.id}/beneficiaires`" class="flex h-11 w-full items-center justify-center rounded-xl border border-slate-300 font-semibold text-slate-700 transition hover:border-amber-700 hover:text-amber-800">Voir les bénéficiaires</RouterLink>
            <RouterLink :to="`/agent/campagnes/${campaign.id}/formulaire`" class="flex h-11 w-full items-center justify-center rounded-xl bg-amber-700 font-semibold text-white transition hover:bg-amber-800">+ Enregistrer</RouterLink>
          </div>
        </div>
      </article>
    </div>
    <div v-if="!loading && !filteredCampaigns.length" class="rounded-2xl border border-dashed border-slate-300 bg-white p-10 text-center text-sm text-slate-500">Aucune campagne ne vous est disponible.</div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from "vue"
import { RouterLink } from "vue-router"
import AlertMessage from "@/components/ui/AlertMessage.vue"
import LoadingSpinner from "@/components/ui/LoadingSpinner.vue"
import { useCampaignStore } from "@/stores/campaign.js"
import { useBeneficiaryStore } from "@/stores/beneficiary.js"

const campaignStore = useCampaignStore()
const beneficiaryStore = useBeneficiaryStore()
const search = ref("")
const loading = ref(false)
const error = ref("")

const statusLabel = (statut) => {
  switch (statut) {
    case "EN_COURS": return "En cours"
    case "TERMINE": return "Terminée"
    case "EN_ATTENTE": return "Planifiée"
    default: return statut || "En cours"
  }
}

const statusClass = (statut) => {
  switch (statut) {
    case "EN_COURS": return "bg-emerald-100 text-emerald-800"
    case "TERMINE": return "bg-slate-100 text-slate-700"
    case "EN_ATTENTE": return "bg-amber-100 text-amber-800"
    default: return "bg-slate-100 text-slate-700"
  }
}

const formatDate = (value) => value ? new Date(value).toLocaleDateString("fr-FR") : "-"

const campaigns = computed(() => campaignStore.campaigns)
const filteredCampaigns = computed(() => {
  const q = search.value.toLowerCase()
  if (!q) return campaigns.value
  return campaigns.value.filter((c) =>
    (c.nom || "").toLowerCase().includes(q) ||
    (c.projet || "").toLowerCase().includes(q) ||
    (c.code_campagne || "").toLowerCase().includes(q)
  )
})

onMounted(async () => {
  loading.value = true
  try {
    await Promise.all([campaignStore.fetchAgentCampaigns(), beneficiaryStore.fetchBeneficiaries()])
  } catch (err) {
    error.value = "Impossible de charger vos campagnes."
  } finally {
    loading.value = false
  }
})
</script>