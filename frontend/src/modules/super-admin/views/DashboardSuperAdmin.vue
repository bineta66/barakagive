<template>
  <div class="space-y-6">
    <header class="flex flex-col gap-3 sm:flex-row sm:items-end sm:justify-between">
      <div>
        <h1 class="text-2xl font-bold text-slate-900">Tableau de bord</h1>
        <p class="mt-1 text-sm text-slate-500">Vue d’ensemble de la plateforme BarakaGive360</p>
      </div>
      <p v-if="dashboard?.updated_at" class="text-xs text-slate-500">Mis à jour le {{ formatDateTime(dashboard.updated_at) }}</p>
    </header>

    <AlertMessage v-if="dashboardError" type="error" :message="dashboardError" :dismissible="true" @dismiss="dashboardError = null" />
    <LoadingSpinner v-if="dashboardLoading && !dashboard" message="Chargement des données de la plateforme..." />

    <template v-if="dashboard">
      <section aria-label="Indicateurs globaux" class="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <KpiCard titre="Total ONG" :valeur="dashboard.ongs.total" :icone="Building2" couleur="bleu-nuit" />
        <KpiCard titre="ONG actives" :valeur="dashboard.ongs.actives" :icone="Building2" couleur="bleu-accent" />
        <KpiCard titre="Demandes en attente" :valeur="dashboard.ongs.pending" :icone="FileText" couleur="rose-baraka" />
        <KpiCard titre="Gérants actifs" :valeur="dashboard.gerants.actifs" :icone="Users" couleur="bleu-nuit" />
      </section>

      <section aria-label="Évolution et activité récente" class="grid min-w-0 grid-cols-1 gap-5 xl:grid-cols-[minmax(0,1.7fr)_minmax(18rem,1fr)]">
        <article class="min-w-0 rounded-xl border border-slate-200/60 bg-white p-5">
          <div class="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
            <div><h2 class="text-lg font-semibold text-slate-900">Évolution des activités</h2><p class="mt-1 text-sm text-slate-500">Évolution des projets, campagnes et bénéficiaires sur la période sélectionnée.</p></div>
            <label class="text-xs font-medium text-slate-600">Période<select v-model="period" class="ml-2 rounded-lg border border-slate-200 bg-white px-2 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-bleu-nuit/30"><option value="7d">7 jours</option><option value="30d">30 jours</option><option value="3m">3 mois</option><option value="6m">6 mois</option><option value="1y">1 an</option></select></label>
          </div>
          <LoadingSpinner v-if="dashboardLoading" message="Mise à jour du graphique..." />
          <DashboardChart v-else-if="evolutionData.labels.length" class="mt-4" type="line" :data="evolutionData" :height="340" :axis-color="chartPalette.primary" :legend-color="chartPalette.primary" grid-color="#E7EEF0" />
          <EmptyState v-else titre="Aucune donnée" description="Aucune création sur cette période." container-class="mt-4 min-h-[180px]" />
        </article>

        <article class="min-w-0 overflow-hidden rounded-xl border border-slate-200/60 bg-white">
          <div class="border-b border-slate-100 px-5 py-4">
            <h2 class="text-lg font-semibold text-slate-900">Activité récente</h2>
            <p class="mt-1 text-xs text-slate-500">Les 8 dernières actions enregistrées.</p>
          </div>
          <div v-if="recentActivities.length" class="max-h-[390px] divide-y divide-slate-100 overflow-y-auto">
            <div v-for="(activity, index) in recentActivities" :key="`${activity.type}-${activity.date}-${index}`" class="flex flex-col gap-1 px-5 py-3">
              <p class="text-sm font-medium text-slate-900">{{ activity.type }}<span v-if="activity.sujet"> : {{ activity.sujet }}</span></p>
              <p v-if="activity.acteur" class="text-xs text-slate-500">{{ activity.acteur }}</p>
              <time class="text-xs text-slate-400">{{ formatDateTime(activity.date) }}</time>
            </div>
          </div>
          <EmptyState v-else titre="Aucune activité récente" description="Les nouvelles actions apparaîtront ici." />
        </article>
      </section>

      <section aria-label="Répartition et statuts de la plateforme" class="grid grid-cols-1 gap-5 xl:grid-cols-2">
        <article class="min-w-0 rounded-xl border border-slate-200/60 bg-white p-5">
          <h2 class="text-base font-semibold" :style="{ color: chartPalette.primary }">ONG par région</h2>
          <p class="mt-1 text-xs text-slate-500">Répartition selon les régions renseignées pour les ONG.</p>
          <DashboardChart
            v-if="regionChartData.labels.length"
            class="mt-3"
            type="bar"
            :data="regionChartData"
            :height="regionChartHeight"
            :horizontal="true"
            axis-color="#00313C"
            legend-color="#00313C"
            series-color="#00313C"
            grid-color="#E7EEF0"
          />
          <EmptyState v-else titre="Aucune région renseignée" description="Les régions apparaîtront ici lorsqu’elles seront présentes dans les fiches ONG." container-class="mt-3 min-h-[180px]" />
        </article>

        <article v-for="panel in statusPanels" :key="panel.key" class="rounded-xl border border-slate-200/60 bg-white p-5">
          <h2 class="text-base font-semibold" :style="{ color: chartPalette.primary }">{{ panel.title }}</h2>
          <div v-if="panel.entries.length" class="mt-3 grid items-center gap-2 sm:grid-cols-[minmax(0,1fr)_minmax(0,1fr)] xl:grid-cols-1 2xl:grid-cols-[minmax(0,1fr)_minmax(0,1fr)]">
            <DashboardChart type="doughnut" :data="statusChartData(panel)" :height="185" />
            <ul class="space-y-2">
              <li v-for="entry in panel.entries" :key="entry.code" class="flex items-center justify-between gap-2 text-xs">
                <span class="flex min-w-0 items-center gap-2" :style="{ color: chartPalette.primary }"><span class="h-2.5 w-2.5 shrink-0 rounded-full" :style="{ backgroundColor: entry.color }" />{{ entry.label }}</span>
                <span class="font-semibold" :style="{ color: chartPalette.primary }">{{ entry.count }}</span>
              </li>
            </ul>
          </div>
          <p v-else class="mt-4 text-sm text-slate-500">Aucune donnée disponible.</p>
        </article>
      </section>

      <section class="grid grid-cols-1 gap-5 xl:grid-cols-2">
        <article class="overflow-hidden rounded-xl border border-slate-200/60 bg-white">
          <div class="flex items-center justify-between border-b border-slate-100 px-5 py-4"><div><h2 class="text-lg font-semibold text-slate-900">Derniers projets</h2><p class="mt-1 text-xs text-slate-500">Projets créés récemment.</p></div><button v-if="dashboard.projets.derniers.length > 8" type="button" class="text-xs font-semibold text-bleu-nuit hover:underline focus:outline-none focus:ring-2 focus:ring-bleu-nuit/30" @click="showAllProjects = !showAllProjects">{{ showAllProjects ? 'Réduire' : 'Voir tout' }}</button></div>
          <div v-if="dashboard.projets.derniers.length" class="divide-y divide-slate-100">
            <div v-for="project in visibleProjects" :key="project.id" class="grid grid-cols-1 gap-1 px-5 py-3 text-sm sm:grid-cols-[1fr_auto] sm:items-center"><div class="min-w-0"><p class="truncate font-semibold text-slate-900">{{ project.name }} <span class="font-normal text-slate-500">· {{ project.code || '—' }}</span></p><p class="mt-0.5 text-xs text-slate-500">{{ project.organization__name || '—' }}</p></div><div class="flex items-center gap-3"><StatusBadge :statut="project.archived ? 'ARCHIVE' : 'ACTIVE'">{{ project.archived ? 'Archivé' : 'Non archivé' }}</StatusBadge><span class="text-xs text-slate-500">{{ formatDate(project.created_at) }}</span></div></div>
          </div>
          <EmptyState v-else titre="Aucun projet" description="Les projets récents apparaîtront ici." />
        </article>

        <article class="overflow-hidden rounded-xl border border-slate-200/60 bg-white">
          <div class="flex items-center justify-between border-b border-slate-100 px-5 py-4"><div><h2 class="text-lg font-semibold text-slate-900">Dernières campagnes pilotes</h2><p class="mt-1 text-xs text-slate-500">Campagnes créées récemment.</p></div><button v-if="dashboard.campagnes.dernieres.length > 8" type="button" class="text-xs font-semibold text-bleu-nuit hover:underline focus:outline-none focus:ring-2 focus:ring-bleu-nuit/30" @click="showAllCampaigns = !showAllCampaigns">{{ showAllCampaigns ? 'Réduire' : 'Voir tout' }}</button></div>
          <div v-if="dashboard.campagnes.dernieres.length" class="divide-y divide-slate-100">
            <div v-for="campaign in visibleCampaigns" :key="campaign.id" class="grid grid-cols-1 gap-1 px-5 py-3 text-sm sm:grid-cols-[1fr_auto] sm:items-center"><div class="min-w-0"><p class="truncate font-semibold text-slate-900">{{ campaign.nom }}</p><p class="mt-0.5 text-xs text-slate-500">Projet : {{ campaign.projet__name || '—' }}</p></div><div class="flex items-center gap-3"><StatusBadge :statut="campaign.statut">{{ statusLabel(campaign.statut) }}</StatusBadge><span class="text-xs text-slate-500">{{ formatDate(campaign.created_at) }}</span></div></div>
          </div>
          <EmptyState v-else titre="Aucune campagne" description="Les campagnes récentes apparaîtront ici." />
        </article>
      </section>

      <article class="overflow-hidden rounded-xl border border-slate-200/60 bg-white">
        <div class="flex items-center justify-between border-b border-slate-100 px-5 py-4"><div><h2 class="text-lg font-semibold text-slate-900">Demandes ONG en attente</h2><p class="mt-1 text-xs text-slate-500">{{ dashboard.demandes_recentes.length }} demandes récentes à traiter.</p></div><RouterLink to="/super-admin/demandes" class="text-xs font-semibold text-bleu-nuit hover:underline focus:outline-none focus:ring-2 focus:ring-bleu-nuit/30">Voir les demandes</RouterLink></div>
        <div v-if="dashboard.demandes_recentes.length" class="grid grid-cols-1 divide-y divide-slate-100 md:grid-cols-2 md:divide-x md:divide-y-0">
          <div v-for="request in dashboard.demandes_recentes" :key="request.id" class="flex items-center justify-between gap-3 px-5 py-3"><div class="min-w-0"><p class="truncate text-sm font-semibold text-slate-900">{{ request.nom_ong }}</p><p class="truncate text-xs text-slate-500">{{ request.email }} · {{ request.region || 'Région non renseignée' }}</p></div><time class="shrink-0 text-xs text-slate-500">{{ formatDate(request.created_at) }}</time></div>
        </div>
        <EmptyState v-else titre="Aucune demande en attente" description="Les nouvelles demandes ONG apparaîtront ici." />
      </article>

    </template>
  </div>
</template>

<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { storeToRefs } from 'pinia'
import { Building2, FileText, Users } from 'lucide-vue-next'
import { useSuperAdminStore } from '@/modules/super-admin/stores/superAdminStore.js'
import KpiCard from '@/components/ui/KpiCard.vue'
import StatusBadge from '@/components/ui/StatusBadge.vue'
import DashboardChart from '@/components/ui/DashboardChart.vue'
import LoadingSpinner from '@/components/ui/LoadingSpinner.vue'
import EmptyState from '@/components/ui/EmptyState.vue'
import AlertMessage from '@/components/ui/AlertMessage.vue'
import { SUPER_ADMIN_CHART_COLORS, SUPER_ADMIN_STATUS_COLORS, withChartOpacity } from '@/modules/super-admin/chartPalette.js'

const store = useSuperAdminStore()
const { dashboard, dashboardLoading, dashboardError } = storeToRefs(store)
const period = ref('30d')
const showAllProjects = ref(false)
const showAllCampaigns = ref(false)
const chartPalette = SUPER_ADMIN_CHART_COLORS
const statusLabels = { EN_ATTENTE: 'En attente', ACTIVE: 'Active', REJETEE: 'Rejetée', SUSPENDED: 'Suspendue', BROUILLON: 'Brouillon', PLANIFIER: 'Planifiée', EN_COURS: 'En cours', TERMINE: 'Terminée', ANNULEE: 'Annulée', NON_ARCHIVE: 'Non archivés', ARCHIVE: 'Archivés' }
const evolutionData = computed(() => {
  const evolution = dashboard.value?.evolution || {}
  const base = evolution.projets || []
  return {
    labels: base.map(item => item.date),
    datasets: [
      { label: 'Projets', data: base.map(item => item.count), borderColor: chartPalette.primary, backgroundColor: withChartOpacity(chartPalette.primary), fill: true, tension: 0.35, borderWidth: 2, borderCapStyle: 'round', borderJoinStyle: 'round', pointRadius: 2, pointHoverRadius: 4 },
      { label: 'Campagnes pilotes', data: (evolution.campagnes || []).map(item => item.count), borderColor: chartPalette.accent, backgroundColor: withChartOpacity(chartPalette.accent), fill: true, tension: 0.35, borderWidth: 2, borderCapStyle: 'round', borderJoinStyle: 'round', pointRadius: 2, pointHoverRadius: 4 },
      { label: 'Bénéficiaires', data: (evolution.beneficiaires || []).map(item => item.count), borderColor: chartPalette.blue, backgroundColor: withChartOpacity(chartPalette.blue), fill: true, tension: 0.35, borderWidth: 2, borderCapStyle: 'round', borderJoinStyle: 'round', pointRadius: 2, pointHoverRadius: 4 },
    ],
  }
})
const organizationStatuses = computed(() => Object.entries(dashboard.value?.ongs.par_statut || {}).map(([code, count]) => ({ code, label: statusLabels[code] || code, count })))
const projectStatuses = computed(() => Object.entries(dashboard.value?.projets.par_statut || {}).map(([code, count]) => ({ code, label: statusLabels[code] || code, count })))
const campaignStatuses = computed(() => Object.entries(dashboard.value?.campagnes.par_statut || {}).map(([code, count]) => ({ code, label: statusLabels[code] || code, count })))
const regionEntries = computed(() => (dashboard.value?.ongs.par_region || []).map(item => ({ label: item.region, count: Number(item.total) })))
const regionChartHeight = computed(() => Math.min(420, Math.max(220, regionEntries.value.length * 28)))
const regionChartData = computed(() => ({
  labels: regionEntries.value.map(item => item.label),
  datasets: [{ label: 'ONG', data: regionEntries.value.map(item => item.count), backgroundColor: chartPalette.primary, borderRadius: 5, maxBarThickness: 18 }],
}))
const statusPanels = computed(() => [
  { key: 'organizations', title: 'ONG par statut', entries: organizationStatuses.value },
  { key: 'projects', title: 'Projets par statut', entries: projectStatuses.value },
  { key: 'campaigns', title: 'Campagnes par statut', entries: campaignStatuses.value },
].map(panel => ({ ...panel, entries: panel.entries.map(entry => ({ ...entry, color: SUPER_ADMIN_STATUS_COLORS[panel.key][entry.code] || chartPalette.primary })) })))
const statusChartData = panel => ({ labels: panel.entries.map(entry => entry.label), datasets: [{ data: panel.entries.map(entry => entry.count), backgroundColor: panel.entries.map(entry => entry.color), borderColor: '#FFFFFF', borderWidth: 2, hoverOffset: 4 }] })
const visibleProjects = computed(() => showAllProjects.value ? dashboard.value?.projets.derniers || [] : (dashboard.value?.projets.derniers || []).slice(0, 8))
const visibleCampaigns = computed(() => showAllCampaigns.value ? dashboard.value?.campagnes.dernieres || [] : (dashboard.value?.campagnes.dernieres || []).slice(0, 8))
const recentActivities = computed(() => (dashboard.value?.activites_recentes || []).slice(0, 8))
const formatDate = value => value ? new Date(value).toLocaleDateString('fr-FR') : '—'
const formatDateTime = value => value ? new Date(value).toLocaleString('fr-FR', { dateStyle: 'short', timeStyle: 'short' }) : '—'
const statusLabel = status => statusLabels[status] || status || '—'
watch(period, value => store.fetchDashboard(value).catch(() => {}))
onMounted(() => store.fetchDashboard(period.value).catch(() => {}))
</script>
