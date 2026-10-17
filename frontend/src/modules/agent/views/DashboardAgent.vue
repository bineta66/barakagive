<template>
  <main class="mx-auto max-w-5xl space-y-5 px-4 py-5 sm:px-6">
    <header class="flex flex-wrap items-center justify-between gap-3">
      <div><p class="text-xs font-bold uppercase tracking-widest text-bleu-nuit">Espace terrain</p><h1 class="mt-1 text-2xl font-bold text-slate-900">Bonjour {{ firstName }}</h1><p class="mt-1 text-sm text-slate-600">Vos campagnes et collectes en un coup d’œil.</p></div>
      <div class="flex flex-wrap items-center gap-2">
        <RouterLink to="/agent/zones" class="min-h-11 rounded-xl bg-bleu-nuit px-4 py-3 text-sm font-bold text-white transition hover:bg-[#00262f] active:scale-[0.98] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-bleu-nuit focus-visible:ring-offset-2">Mes zones</RouterLink>
        <span class="rounded-full px-3 py-2 text-sm font-semibold" :class="isOnline ? 'bg-emerald-50 text-emerald-800' : 'bg-bleu-nuit/10 text-bleu-nuit'">{{ isOnline ? 'En ligne' : 'Hors connexion' }}</span>
      </div>
    </header>
    <p v-if="error" class="rounded-lg bg-red-50 p-3 text-sm text-red-800">{{ error }}</p>
    <div class="grid grid-cols-2 gap-3 sm:grid-cols-4 sm:gap-4">
      <article v-for="item in kpis" :key="item.label" class="rounded-2xl border border-slate-200 bg-white p-4 shadow-sm sm:p-5">
        <p class="text-sm font-medium text-slate-600">{{ item.label }}</p><p class="mt-2 text-3xl font-bold text-slate-900">{{ loading ? '…' : (dashboard[item.key] ?? 0) }}</p>
      </article>
    </div>
    <section class="rounded-2xl border border-slate-200 bg-white p-4 sm:p-5">
      <div class="flex items-center justify-between gap-3"><div><h2 class="font-bold text-slate-900">Mes campagnes actives</h2><p class="text-sm text-slate-500">Campagnes qui vous sont affectées aujourd’hui.</p></div><RouterLink to="/agent/campagnes" class="rounded-xl border px-4 py-2 text-sm font-semibold text-slate-800">Toutes</RouterLink></div>
      <div v-if="campaigns.length" class="mt-4 divide-y divide-slate-100">
        <article v-for="campaign in campaigns.slice(0, 3)" :key="campaign.id" class="flex flex-wrap items-center justify-between gap-3 py-3">
          <div class="min-w-0"><h3 class="truncate font-semibold text-slate-900">{{ campaign.nom }}</h3><p class="text-sm text-slate-500">{{ campaign.projet }} · {{ campaign.zone || 'Zone à confirmer' }}</p></div>
          <RouterLink :to="`/agent/campagnes/${campaign.id}/formulaire`" class="min-h-11 rounded-xl bg-bleu-nuit px-4 py-3 text-sm font-bold text-white transition hover:bg-[#00262f] active:scale-[0.98] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-bleu-nuit focus-visible:ring-offset-2">Continuer la collecte</RouterLink>
        </article>
      </div>
      <p v-else-if="!loading" class="mt-4 rounded-xl bg-slate-50 p-4 text-sm text-slate-600">Aucune campagne active ne vous est affectée aujourd’hui.</p>
    </section>
    <section class="rounded-2xl border border-slate-200 bg-white p-4 sm:p-5">
      <div class="flex items-center justify-between gap-3"><div><h2 class="font-bold text-slate-900">Synchronisation</h2><p class="text-sm text-slate-500">Les formulaires en attente restent enregistrés sur cet appareil.</p></div><RouterLink to="/agent/synchronisation" class="min-h-11 rounded-xl border px-4 py-3 text-sm font-semibold">Voir l’état</RouterLink></div>
    </section>
  </main>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { RouterLink } from 'vue-router'
import api from '@/services/api.js'
import { useAuthStore } from '@/stores/auth.js'
import { useCampaignStore } from '@/stores/campaign.js'
import { useOnlineStatus } from '@/composables/useOnlineStatus.js'

const auth = useAuthStore(), campaignStore = useCampaignStore()
const { isOnline } = useOnlineStatus()
const dashboard = ref({}), loading = ref(true), error = ref('')
const firstName = computed(() => (auth.user?.first_name || auth.user?.full_name || 'Agent').split(' ')[0])
const campaigns = computed(() => {
  const today = new Date().toISOString().slice(0, 10)
  return campaignStore.campaigns.filter(c => c.date_debut <= today && c.date_fin >= today && !['TERMINE', 'ANNULEE'].includes(c.statut))
})
const kpis = [
  { label: 'Mes campagnes', key: 'campagnes_actives' },
  { label: 'Mes zones', key: 'zones_assignees' },
  { label: 'Bénéficiaires collectés', key: 'beneficiaires_enregistres' },
  { label: 'Bénéficiaires prioritaires', key: 'beneficiaires_prioritaires' },
]
onMounted(async () => {
  try {
    const [, response] = await Promise.all([
      campaignStore.fetchAgentCampaigns(),
      api.get('/api/agent/dashboard/'),
    ])
    dashboard.value = response.data || {}
  } catch {
    error.value = isOnline.value ? 'Impossible de charger le tableau de bord.' : 'Tableau de bord indisponible hors connexion. Vos collectes locales restent accessibles via Synchronisation.'
  } finally { loading.value = false }
})
</script>
