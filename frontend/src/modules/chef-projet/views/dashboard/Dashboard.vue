<template>
  <main class="min-h-screen space-y-6 bg-slate-50 p-4 sm:p-6">
    <header>
      <h1 class="text-3xl font-bold text-bleu-nuit">Tableau de bord</h1>
      <p class="mt-1 text-sm text-slate-500">Pilotage operationnel des projets affectes.</p>
    </header>

    <AlertMessage v-if="error" type="error" :message="error" />
    <LoadingSpinner v-if="loading" message="Chargement des donnees du projet..." />

    <template v-if="decision">
      <section class="grid grid-cols-1 gap-3 sm:grid-cols-2 xl:grid-cols-4">
        <KpiCard titre="Projets actifs" :valeur="op.projets_actifs" :icone="FolderKanban" />
        <KpiCard titre="Campagnes" :valeur="op.campagnes" :icone="ClipboardList" />
        <KpiCard titre="Beneficiaires" :valeur="op.beneficiaires" :icone="Users" />
        <KpiCard titre="Beneficiaires prioritaires" :valeur="op.beneficiaires_prioritaires" :icone="ShieldAlert" couleur="red" />
      </section>

      <section class="grid grid-cols-1 gap-3 rounded-xl border border-slate-200 bg-white p-4 sm:grid-cols-2 xl:grid-cols-5">
      <label class="block"><span class="sr-only">Projet</span>
        <select v-model="filters.project_id" class="filter-control" @change="onProjectChange">
          <option value="">Tous les projets</option><option v-for="p in options.projets" :key="p.id" :value="String(p.id)">{{ p.name }}</option>
        </select>
      </label>
      <label class="block"><span class="sr-only">Campagne</span>
        <select v-model="filters.campaign_id" class="filter-control" @change="onCampaignChange">
          <option value="">Toutes les campagnes</option><option v-for="c in filteredCampaigns" :key="c.id" :value="String(c.id)">{{ c.nom }}</option>
        </select>
      </label>
      <label class="block"><span class="sr-only">Region</span>
        <select v-model="filters.region_id" class="filter-control" @change="onRegionChange">
          <option value="">Toutes les regions</option><option v-for="r in options.regions" :key="r.id" :value="String(r.id)">{{ r.nom }}</option>
        </select>
      </label>
      <label class="block"><span class="sr-only">Zone</span>
        <select v-model="filters.zone_id" class="filter-control" @change="refresh">
          <option value="">Toutes les zones</option><option v-for="z in filteredZones" :key="z.id" :value="z.id">{{ z.nom }}</option>
        </select>
      </label>
      <label class="block"><span class="sr-only">Periode</span>
        <select v-model="period" class="filter-control" @change="onPeriodChange">
          <option value="year">Cette annee</option><option value="90days">90 derniers jours</option><option value="all">Toute periode</option><option value="custom">Personnalisee</option>
        </select>
      </label>
      <template v-if="period === 'custom'">
        <label class="space-y-1 text-xs font-semibold text-slate-600">Date debut<input v-model="filters.start_date" type="date" class="filter-control" @change="refresh" /></label>
        <label class="space-y-1 text-xs font-semibold text-slate-600">Date fin<input v-model="filters.end_date" type="date" class="filter-control" @change="refresh" /></label>
      </template>
    </section>

      <section class="grid grid-cols-1 gap-4 xl:grid-cols-2">
        <article class="panel">
          <h2 class="panel-title">Situation financiere</h2>
          <p class="mb-4 text-xs text-slate-500">Les financements recus et depenses approuvees sont calcules par Django.</p>
          <DashboardChart v-if="financeChartData.datasets[0].data.some(value => value !== 0)" type="bar" :data="financeChartData" :height="280" horizontal value-format="currency" />
          <EmptyState v-else titre="Aucune donnee disponible" description="Aucun budget ou mouvement financier pour ce filtre." container-class="min-h-[180px]" />
          <p class="mt-3 text-xs text-slate-500">Solde = financements recus + dons recus - depenses validees. Le budget est rattache au projet et ne peut pas etre ventile par zone.</p>
        </article>
        <article class="panel">
          <h2 class="panel-title">Beneficiaires par zone</h2>
          <DashboardChart v-if="zoneChartData.labels.length" type="bar" :data="zoneChartData" :height="280" />
          <EmptyState v-else titre="Aucune donnee disponible" description="Aucun beneficiaire par zone dans ce filtre." container-class="min-h-[180px]" />
        </article>
      </section>

      <section class="panel">
        <h2 class="panel-title">Projets et campagnes</h2>
        <p class="mt-1 text-xs text-slate-500">Nombre de projets et de campagnes par projet affect?.</p>
        <DashboardChart v-if="projectCampaignChartData.labels.length" class="mt-4" type="bar" :data="projectCampaignChartData" :height="300" />
        <EmptyState v-else titre="Aucune donn?e disponible" description="Aucun projet ou campagne ne correspond aux filtres." container-class="mt-4 min-h-[180px]" />
      </section>

      <section class="panel">
        <h2 class="panel-title">Taux de prise en charge par niveau de bénéficiaire</h2>
        <p class="mt-1 text-xs text-slate-500">Répartition calculée selon le statut actuel des bénéficiaires.</p>
        <div class="mt-4 grid grid-cols-1 gap-4 sm:grid-cols-3">
          <article v-for="level in beneficiaryLevelItems" :key="level.label" class="flex flex-col items-center rounded-xl border border-slate-100 bg-white p-4">
            <DashboardChart type="doughnut" :data="progressChartData(level.value, level.color)" :height="150" :center-value="level.value" center-label="du total" />
            <p class="mt-2 text-sm font-semibold text-slate-800">{{ level.label }}</p>
            <p class="mt-1 text-xs text-slate-500">{{ level.count }} bénéficiaire(s)</p>
          </article>
        </div>
      </section>
    </template>
  </main>
</template>

<script setup>
import { computed, reactive, ref } from 'vue'
import { FolderKanban, ClipboardList, Users, ShieldAlert } from 'lucide-vue-next'
import dayjs from 'dayjs'
import 'dayjs/locale/fr'
import AlertMessage from '@/components/ui/AlertMessage.vue'
import LoadingSpinner from '@/components/ui/LoadingSpinner.vue'
import KpiCard from '@/components/ui/KpiCard.vue'
import EmptyState from '@/components/ui/EmptyState.vue'
import DashboardChart from '@/components/ui/DashboardChart.vue'
import { useProjectStore } from '@/stores/project.js'
import { useAutoRefresh } from '@/composables/useAutoRefresh.js'

const store = useProjectStore()
dayjs.locale('fr')
const decision = computed(() => store.decisionDashboard)
const op = computed(() => decision.value?.operationnel || {})
const finance = computed(() => decision.value?.finance || {})
const options = computed(() => decision.value?.filtres || { projets: [], campagnes: [], regions: [], zones: [] })
const filters = reactive({ project_id: '', campaign_id: '', region_id: '', zone_id: '', start_date: dayjs().startOf('year').format('YYYY-MM-DD'), end_date: dayjs().format('YYYY-MM-DD') })
const period = ref('year')
const loading = ref(false)
const error = ref('')
const filteredCampaigns = computed(() => options.value.campagnes.filter(c => !filters.project_id || String(c.projet_id) === String(filters.project_id)))
const filteredZones = computed(() => options.value.zones.filter(z => !filters.region_id || String(z.region_id) === String(filters.region_id)))
const financeChartData = computed(() => ({
  labels: ['Budget total', 'Financements recus', 'Dons recus', 'Depenses validees', 'Solde disponible'],
  datasets: [{
    data: [finance.value.budget_total, finance.value.financements_recus, finance.value.dons_recus, finance.value.depenses_validees, finance.value.solde].map(Number),
    backgroundColor: ['#94a3b8', '#021427', '#16a34a', '#f59e0b', Number(finance.value.solde) < 0 ? '#dc2626' : '#0ea5e9'],
    borderRadius: 5,
  }],
}))
const zoneChartData = computed(() => {
  const rows = decision.value?.graphiques.beneficiaires_zones || []
  return {
    labels: rows.map(row => row.nom),
    datasets: [
      { label: 'Total', data: rows.map(row => row.total), backgroundColor: '#021427', borderRadius: 4 },
      { label: 'Prioritaires', data: rows.map(row => row.priority), backgroundColor: '#dc2626', borderRadius: 4 },
      { label: 'Pris en charge', data: rows.map(row => row.aided), backgroundColor: '#16a34a', borderRadius: 4 },
    ],
  }
})
const projectCampaignChartData = computed(() => {
  const projects = options.value.projets.filter(project => !filters.project_id || String(project.id) === String(filters.project_id))
  const campaigns = options.value.campagnes.filter(campaign => !filters.campaign_id || String(campaign.id) === String(filters.campaign_id))
  return {
    labels: projects.map(project => project.name),
    datasets: [
      { label: 'Projets', data: projects.map(() => 1), backgroundColor: '#021427', borderRadius: 4 },
      { label: 'Campagnes', data: projects.map(project => campaigns.filter(campaign => String(campaign.projet_id) === String(project.id)).length), backgroundColor: '#1A6FAD', borderRadius: 4 },
    ],
  }
})
const beneficiaryLevelItems = computed(() => {
  const levels = decision.value?.beneficiaires_par_niveau || {}
  return [
    { label: 'Évalués', value: Number(levels.taux_evalues) || 0, count: Number(levels.evalues) || 0, color: '#2563EB' },
    { label: 'Prioritaires', value: Number(levels.taux_prioritaires) || 0, count: Number(levels.prioritaires) || 0, color: '#F97316' },
    { label: 'Pris en charge', value: Number(levels.taux_pris_en_charge) || 0, count: Number(levels.pris_en_charge) || 0, color: '#16A36A' },
  ]
})
const progressChartData = (value, color = '#00313C') => {
  const percent = Math.min(100, Math.max(0, Number(value) || 0))
  return { datasets: [{ data: [percent, 100 - percent], backgroundColor: [color, '#e2e8f0'], borderWidth: 0, hoverOffset: 0 }] }
}
const refresh = async () => {
  loading.value = true
  error.value = ''
  try { await store.fetchDecisionDashboard({ ...filters }) }
  catch (e) { error.value = e?.response?.data?.detail || 'Impossible de charger le tableau de bord.' }
  finally { loading.value = false }
}
const onProjectChange = () => { filters.campaign_id = ''; filters.region_id = ''; filters.zone_id = ''; refresh() }
const onCampaignChange = () => { filters.region_id = ''; filters.zone_id = ''; refresh() }
const onRegionChange = () => { filters.zone_id = ''; refresh() }
const onPeriodChange = () => {
  const today = dayjs()
  if (period.value === 'year') { filters.start_date = today.startOf('year').format('YYYY-MM-DD'); filters.end_date = today.format('YYYY-MM-DD') }
  else if (period.value === '90days') { filters.start_date = today.subtract(89, 'day').format('YYYY-MM-DD'); filters.end_date = today.format('YYYY-MM-DD') }
  else if (period.value === 'all') { filters.start_date = ''; filters.end_date = '' }
  refresh()
}
useAutoRefresh(refresh)
</script>

<style scoped>
.filter-control { @apply mt-1 block w-full rounded-xl border border-white/70 bg-white/65 px-3 py-2 text-sm font-normal text-slate-800 backdrop-blur-lg transition-all duration-200 focus:border-bleu-accent/50 focus:outline-none focus:ring-2 focus:ring-bleu-accent/20; }
.panel { @apply rounded-2xl border border-white/70 bg-white/70 p-5 backdrop-blur-xl transition-all duration-300; }
.panel-title { @apply text-base font-bold text-slate-900; }
.empty-state { @apply mt-4 rounded-lg bg-slate-50 px-3 py-4 text-sm text-slate-500; }
.legend-dot { @apply mr-1 inline-block size-2.5 rounded-full; }
.primary-button { @apply inline-flex items-center gap-2 rounded-lg bg-bleu-nuit px-4 py-2.5 text-sm font-semibold text-white disabled:cursor-not-allowed disabled:opacity-50; }
.secondary-button { @apply inline-flex items-center gap-2 rounded-lg border border-slate-200 px-3 py-2 text-sm font-medium text-slate-700 disabled:opacity-50; }
</style>


