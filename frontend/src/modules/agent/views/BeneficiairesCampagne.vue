<template>
  <div class="mx-auto max-w-7xl space-y-6 px-4 py-5 md:px-6">
    <div class="flex items-center justify-between gap-3">
      <div><p class="text-xs font-bold uppercase tracking-[0.18em] text-amber-700">Collecte terrain</p><h1 class="mt-1 text-2xl font-bold text-slate-900">Bénéficiaires</h1><p class="mt-1 text-sm text-slate-500">{{ campaign?.nom || "Campagne" }}</p></div>
      <RouterLink :to="`/agent/campagnes/${route.params.id}/formulaire`" class="flex h-11 items-center rounded-xl bg-amber-700 px-4 text-sm font-bold text-white">+ Enregistrer</RouterLink>
    </div>
    <AlertMessage v-if="error" type="error" :message="error" />
    <div v-if="!loading" class="overflow-hidden rounded-2xl border border-gray-200 bg-white">
      <div class="grid grid-cols-1 gap-4 p-4 md:hidden">
        <article v-for="item in beneficiaries" :key="item.id" class="rounded-xl border border-slate-200 p-4"><div class="flex items-start justify-between"><div><h2 class="font-bold text-slate-900">{{ item.prenom }} {{ item.nom }}</h2><p class="mt-1 text-sm text-slate-500">{{ item.telephone || "Téléphone non renseigné" }}</p></div><span class="rounded-full bg-emerald-50 px-2 py-1 text-xs font-semibold text-emerald-700">{{ item.sync_status || "Synchronisé" }}</span></div><div class="mt-3 grid grid-cols-2 gap-2 text-xs text-slate-500"><span>Sexe : {{ item.sexe }}</span><span>Localité : {{ item.zone?.nom || "-" }}</span><span>Date : {{ formatDate(item.created_at) }}</span></div><div class="mt-4 flex gap-2"><RouterLink :to="`/agent/beneficiaires/${item.id}`" class="flex-1 rounded-lg border border-slate-300 py-2 text-center text-xs font-semibold">Voir détail</RouterLink><button type="button" class="flex-1 rounded-lg bg-slate-100 py-2 text-xs font-semibold text-slate-500" disabled>Modifier</button></div></article>
      </div>
      <div class="hidden overflow-x-auto md:block"><table class="w-full text-left text-sm"><thead class="bg-slate-50 text-xs uppercase text-slate-500"><tr><th class="px-5 py-3">Nom</th><th class="px-5 py-3">Téléphone</th><th class="px-5 py-3">Sexe</th><th class="px-5 py-3">Localité</th><th class="px-5 py-3">Date</th><th class="px-5 py-3">Statut</th><th class="px-5 py-3"></th></tr></thead><tbody class="divide-y divide-slate-100"><tr v-for="item in beneficiaries" :key="item.id"><td class="px-5 py-4 font-semibold">{{ item.prenom }} {{ item.nom }}</td><td class="px-5 py-4">{{ item.telephone || "-" }}</td><td class="px-5 py-4">{{ item.sexe }}</td><td class="px-5 py-4">{{ item.zone?.nom || "-" }}</td><td class="px-5 py-4">{{ formatDate(item.created_at) }}</td><td class="px-5 py-4"><span class="rounded-full bg-emerald-50 px-2 py-1 text-xs font-semibold text-emerald-700">{{ item.sync_status || "Synchronisé" }}</span></td><td class="px-5 py-4 text-right"><RouterLink :to="`/agent/beneficiaires/${item.id}`" class="font-semibold text-amber-700">Détail</RouterLink></td></tr></tbody></table></div>
      <div v-if="!beneficiaries.length" class="p-10 text-center text-sm text-slate-500">Aucun bénéficiaire pour cette campagne.</div>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from "vue"
import { RouterLink, useRoute } from "vue-router"
import AlertMessage from "@/components/ui/AlertMessage.vue"
import { useCampaignStore } from "@/stores/campaign.js"
import { useBeneficiaryStore } from "@/stores/beneficiary.js"

const route = useRoute()
const campaignStore = useCampaignStore()
const beneficiaryStore = useBeneficiaryStore()
const loading = ref(false)
const error = ref("")
const campaign = computed(() => campaignStore.campaigns.find((item) => String(item.id) === String(route.params.id)))
const beneficiaries = computed(() => beneficiaryStore.beneficiaries.filter((item) => String(item.campagne?.id) === String(route.params.id)))
const formatDate = (value) => value ? new Date(value).toLocaleDateString("fr-FR") : "-"

onMounted(async () => { loading.value = true; try { await Promise.all([campaignStore.fetchCampaigns(), beneficiaryStore.fetchBeneficiaries()]) } catch { error.value = "Impossible de charger les bénéficiaires." } finally { loading.value = false } })
</script>

